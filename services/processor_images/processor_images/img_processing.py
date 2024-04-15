import os
from typing import Union

import aiohttp
import numpy as np
import cv2
from rembg import remove
from processor_images.logging.logger import get_logger

logger = get_logger("PROCESSOR_IMAGES")


def pyramid_images_merging(filename_1: str, filename_2: str) -> np.ndarray:
    """
    Функция для слияния двух изображений с помощью пирамиды Лапласа.

    :param filename_1: Полный путь до первого изображения.
    :param filename_2: Полный путь до второго изображения.
    :return: np.ndarray представление результирующего изображения.
    """
    param_sampling = int(os.getenv("PYRAMID_DEPTH"))
    size_of_resize = int(os.getenv("RESIZE_SIZE"))
    A = cv2.resize(cv2.imread(filename_1), (size_of_resize, size_of_resize))
    B = cv2.resize(cv2.imread(filename_2), (size_of_resize, size_of_resize))
    # generate Gaussian pyramid for A
    G = A.copy()
    gpA = [G]
    for i in range(param_sampling):
        G = cv2.pyrDown(G)
        gpA.append(G)
    # generate Gaussian pyramid for B
    G = B.copy()
    gpB = [G]
    for i in range(param_sampling):
        G = cv2.pyrDown(G)
        gpB.append(G)
    # generate Laplacian Pyramid for A
    lpA = [gpA[param_sampling - 1]]
    for i in range(param_sampling - 1, 0, -1):
        GE = cv2.pyrUp(gpA[i])
        L = cv2.subtract(gpA[i - 1], GE)
        lpA.append(L)
    # generate Laplacian Pyramid for B
    lpB = [gpB[param_sampling - 1]]
    for i in range(param_sampling - 1, 0, -1):
        GE = cv2.pyrUp(gpB[i])
        L = cv2.subtract(gpB[i - 1], GE)
        lpB.append(L)
    LS = []
    for la, lb in zip(lpA, lpB):
        rows, cols, dpt = la.shape
        # Вариант с объединением половинок изображений
        ls = np.hstack((la[:, :cols // 2], lb[:, cols // 2:]))
        LS.append(ls)
    ls_ = LS[0]
    for i in range(1, param_sampling):
        ls_ = cv2.pyrUp(ls_)
        ls_ = cv2.add(ls_, LS[i])
    return ls_


async def prepare_merger(filepathes: dict) -> Union[np.ndarray, None]:
    """
    Функция, принимающая тело запроса, состоящего из путей до изображений.

    :param filepathes: Dictionary вида {"img_path_1": "путь_до_изображения_1",
    "img_path_2": "путь_до_изображения_2"}.
    :return: np.ndarray изображение или None.
    """
    img_path_1 = filepathes.get("img_path_1")
    img_path_2 = filepathes.get("img_path_2")
    if img_path_1 and img_path_2:
        return pyramid_images_merging(img_path_1, img_path_2)
    else:
        logger.info(f"One or more arguments are missing for this function!!!")
        return None


def get_highlighting_unet(file_name_input: str, file_name_output: str) -> None:
    """
    Функция, удаляющая фон из изображения. Использует модель Unet для
    определения объекта на изображении и обнуления всех пикселей в альфа-канале,
    не попадающих в область объекта.

    :param file_name_input: Полный путь до входного изображения.
    :param file_name_output: Полный путь, по которому нужно сохранить результат.
    :return: None.
    """
    output = remove(cv2.imread(file_name_input))
    cv2.imwrite(file_name_output, output)


async def prepare_highlighter(filepath: Union[dict, None] = None):
    """
    Функция, позволяющая удалять фон со всех соскрапленных и еще необработанных
    изображений или только с определенного изображения, путь к которому передан
    в функцию в качестве параметра.

    :param filepath: Dictionary вида {"img_path": "путь_до_изображения"} или
        None.
    :return:
    """
    conn = aiohttp.TCPConnector()
    session = aiohttp.ClientSession(connector=conn)
    highlighted_dir = os.getenv("SAVE_HIGHLIGHTED_DIR")

    try:
        if not filepath:
            async with session.get(
                os.getenv("ALL_HIGHLIGHTED_URL")
            ) as not_highlighted:
                not_highlighted.raise_for_status()
                get_result = await not_highlighted.json()
                try:
                    for record in get_result["answer"]:
                        if not record["is_highlighted"]:
                            img_filename = record["img_path"]
                            get_highlighting_unet(
                                img_filename,
                                (highlighted_dir +
                                 img_filename.split(
                                     "/"
                                 )[-1].replace("jpg", "png"))
                            )
                            record["is_highlighted"] = True
                            await session.post(
                                os.getenv("UPDATE_URL"),
                                json=record
                            )
                            logger.info(
                                f"Image [{record['img_name']}] was "
                                f"successfully highlighted!")
                        else:
                            logger.info(
                                f"Image [{record['img_name']}] is "
                                f"already highlighted! Skip updating!")
                except Exception as e:
                    logger.error(
                        f"Couldn't highlight image [{record['img_name']}]! "
                        f"REASON: {e}"
                    )
            await conn.close()
            await session.close()
        else:
            img = None
            async with session.post(os.getenv('GET_ONE_URL'),
                                    json=filepath) as resp:
                response = await resp.json()
                response = response[0]
                new_img_path = (highlighted_dir +
                                response["img_path"].split("/")[-1][:-4] +
                                ".png")
                if response["is_highlighted"]:
                    img = cv2.imread(new_img_path)
                else:
                    try:
                        get_highlighting_unet(
                            response["img_path"],
                            new_img_path
                        )
                        response["is_highlighted"] = True
                        await session.post(
                            os.getenv("UPDATE_URL"),
                            json=response
                        )
                        img = cv2.imread(new_img_path)
                    except Exception as e:
                        logger.error(
                            f"Couldn't highlight image "
                            f"[{response['img_name']}]! REASON: {e}"
                        )
            await conn.close()
            await session.close()
            return img
    except Exception as e:
        logger.error(f"Got error while processing scraped images. REASON: {e}")
