import os

import cv2
import numpy as np
import aiohttp
from PIL import Image
import torch
from torch.utils.data import DataLoader
import clip
from model_img_search.logging.logger import get_logger
from model_img_search.grid_plot import grid_plot


device = "cuda:0" if torch.cuda.is_available() else "cpu"
test_model, test_preprocess = clip.load("ViT-B/32", device=device, jit=False)

logger = get_logger("CLIP_LOGGER")
highlighted_dir = os.getenv("SAVE_HIGHLIGHTED_DIR")
conn = aiohttp.TCPConnector()
session = aiohttp.ClientSession(connector=conn)


class ImageDataset:
    """
    Класс кастомного датасета для создания эмбеддингов изображений.
    """
    def __init__(self, list_image_path):
        self.image_path = list_image_path

    def __len__(self):
        return len(self.image_path)

    def __getitem__(self, idx):
        image = test_preprocess(Image.open(self.image_path[idx]))
        return image


async def get_top_clip_similar(text_query):
    """
    Функция получения ТОП-25 самых соответствующих текстовому запросу
    изображений.

    :param text_query: Текстовый запрос в формате str.
    :return: Коллаж из ТОП-25 изображений или None.
    """
    text_prompt = text_query.get("text_query")
    if text_prompt:
        text = clip.tokenize(text_prompt.lower()).to(device)
        text_features = test_model.encode_text(text)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        text_features = text_features.squeeze(0).cpu().detach().numpy().tolist()
        async with session.post(os.getenv("GET_TOP_CLIP_SIMILAR_URL"),
                                json={"embedding_list": str(text_features)}
                                ) as top_clip:
            get_result = await top_clip.json()
            list_of_similar_images = [
                record["img_path"]
                for record in get_result["answer"]
            ]
        logger.info("TOP-25 similar images returned successfully!")
        return grid_plot(cv2.imread(list_of_similar_images[0]),
                         list_of_similar_images[1:])
    else:
        return None


def get_clip_embeddings(img_pathes):
    """
    Фукнция для создания эмбеддингов всех изображений, которые еще не были
    обработаны CLIP моделью.

    :param img_pathes: Список полных путей для открытия файлов изображений.
    :return: Список из эмбеддингов всех обработанных CLIP изображений.
    """
    img_arr = None
    dataset = ImageDataset(img_pathes)
    train_dataloader = DataLoader(dataset,
                                  batch_size=len(img_pathes),
                                  shuffle=False)
    logger.info("CLIP STARTED process embedding of batch images!")
    for batch in train_dataloader:
        images = batch
        images = images.to(device)
        with torch.no_grad():
            image_features = test_model.encode_image(images)
        image_features /= image_features.norm(dim=-1, keepdim=True)
        image_features = image_features.squeeze(0).cpu().detach().numpy()
        if img_arr is None:
            img_arr = image_features
        else:
            img_arr = np.concatenate((img_arr, image_features), axis=0)
    img_arr = (img_arr.T / np.linalg.norm(img_arr, axis=1)).T
    logger.info("CLIP ENDED process embedding of batch images!")
    return img_arr.tolist()


async def prepare_clip_search():
    """
    Функция собирающая записи из БД по тем изображениям, которые не были
    обработаны CLIP, и записывающая вычисленные эмбеддинги этих изображений
    в соответствии с id в таблицу в БД.

    :return: Текстовое сообщение об исполнении кода.
    """
    try:
        async with session.get(
                os.getenv("ALL_NOT_EMBEDDED_CLIP_URL")
        ) as not_embedded:
            not_embedded.raise_for_status()
            get_result = await not_embedded.json()
            list_of_ids = [record["id"] for record in get_result["answer"]]
            list_of_path = [record["img_path"]
                            for record in get_result["answer"]]
            res_emb = get_clip_embeddings(list_of_path)
            list_of_ids_embedded_imgs = [(img_id, str(emb)) for img_id, emb in
                                         zip(list_of_ids, res_emb)]
            await session.post(
                os.getenv("UPDATE_CLIP_EMBEDDINGS_URL"),
                json={"list_id_emb": list_of_ids_embedded_imgs}
            )
        return f"Successfully got embeddings from " \
               f"{len(list_of_ids_embedded_imgs)} images!"
    except Exception as e:
        logger.error(f"Got error while computing embeddings of images! "
                     f"REASON: {e}")
        return f"Got error while computing embeddings of images! REASON: {e}"
