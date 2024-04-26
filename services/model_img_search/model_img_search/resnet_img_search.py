import os

import numpy as np
import torch.nn as nn
from torchvision import models, transforms
import cv2
from torchvision.models import ResNet34_Weights
import aiohttp
from model_img_search.logging.logger import get_logger
from model_img_search.grid_plot import grid_plot


logger = get_logger("RESNET_LOGGER")
highlighted_dir = os.getenv("SAVE_HIGHLIGHTED_DIR")
conn = aiohttp.TCPConnector()
session = aiohttp.ClientSession(connector=conn)
model = models.resnet34(weights=ResNet34_Weights.DEFAULT)
model.fc = nn.Identity()
model.eval()

transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])


def get_resnet_embedding(image, img_filename):
    """
    Функция, вычисляющая эмбеддинг переданного на вход изображения с помощью
    предобученного классификатора ResNet34.

    :param image: Изображение в формате np.ndarray.
    :param img_filename: Имя изображения для сообщения логера.
    :return: Список, представляющий собой эмбеддинг переданного изображения.
    """
    input_tensor = transform(image).unsqueeze(0)
    out = model(input_tensor)[0].tolist()
    logger.info(f"Successfully embedded image [{img_filename}]!")
    return out


async def get_top_resnet_similar(init_img):
    """
    Основная функция поиска ТОП-24 похожих на входное изображение изображений
    с помощью предобученной модели ResNet34. Возвращает ТОП-24 в виде коллажа.

    :param init_img: Входное изображение в формате bytes.
    :return: np.array коллаж ТОП-24 похожих изображений.
    """
    init_image = cv2.imdecode(np.frombuffer(init_img, np.uint8),
                              cv2.IMREAD_COLOR)
    cur_embed = get_resnet_embedding(init_image, "MAIN_INIT_REQUEST")
    async with session.post(os.getenv("GET_TOP_RESNET_SIMILAR_URL"),
                            json={"embedding_list": str(cur_embed)}
                            ) as top_resnet:
        get_result = await top_resnet.json()
        list_of_pathes = [record["img_path"] for record in get_result["answer"]]
    logger.info("TOP-24 similar images returned successfully!")
    return grid_plot(init_image, list_of_pathes)


async def prepare_resnet_search():
    """
    Функция, позволяющая вычислить эмбеддинги всех изображений в БД, по которым
    еще не были вычислены эмбеддинги.

    :return: Текст ответа об успешном исполнении или текст ошибки.
    """
    cnt = 0
    try:
        async with session.get(
                os.getenv("ALL_NOT_EMBEDDED_RESNET_URL")
        ) as not_embedded:
            not_embedded.raise_for_status()
            get_result = await not_embedded.json()
            list_of_embedded_imgs = []
            for record in get_result["answer"]:
                cur_embedding = get_resnet_embedding(
                    cv2.imread(record["img_path"]),
                    record["img_path"].split("/")[-1].replace("jpg", "png")
                )
                list_of_embedded_imgs.append((record["id"], str(cur_embedding)))
                cnt += 1
            await session.post(
                os.getenv("UPDATE_RESNET_EMBEDDINGS_URL"),
                json={"list_id_emb": list_of_embedded_imgs}
            )
        return f"Successfully got embeddings from {cnt} images!"
    except Exception as e:
        logger.error(f"Got error while computing embeddings of images! "
                     f"REASON: {e}")
        return f"Got error while computing embeddings of images! REASON: {e}"
