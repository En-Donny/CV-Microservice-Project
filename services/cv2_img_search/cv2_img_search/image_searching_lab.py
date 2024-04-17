import os

import numpy as np
import cv2
from skimage.color import deltaE_ciede2000
from cv2_img_search.logging.logger import get_logger
from cv2_img_search.collage_maker import plot_finded_imgs

logger = get_logger("LAB_SEARCHER_IMAGES")


def bgra_2_laba(img):
    """
    Метод для перевода изображения из BGRa-формата в LABa-формат. Переданное
    изображение не меняется.

    :param img: Изображение, над которым необходимо произвести указанные
        в описании метода действия.
    :return: Возвращает LABa-формат изображения.
    """
    resized_img = cv2.resize(img, (300, 450))
    hsv_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2Lab)
    result = resized_img.copy()
    result[:, :, :3] = hsv_img
    return result.astype(np.float32)


def get_top_similar_imgs(main_img, dir_to_find, top_count=5):
    """
    Функция, позволяющая по переданному в качестве параметра изображению искать
    среди всех остальных обработанных изображений похожие ему по палитре LAB с
    помощью метрики CIEDE2000. Сохраняет все похожие изображения в список,
    который потом передается в функцию plot_finded_imgs для создания
    коллажа из похожих изображений.

    :param main_img: np.ndarray формат входного изображения.
    :param dir_to_find: Директория, в которой необходимо искать похожие
        изображения.
    :param top_count: Количество-топ похожих изображений.
    :return: np.ndarray формат коллажа из комплементарных изображений.
    """
    top_similars = {}
    im1_lab = bgra_2_laba(main_img)
    for img_file in os.listdir(dir_to_find):
        img_in = cv2.imread(dir_to_find + img_file, cv2.IMREAD_UNCHANGED)
        im2_lab = bgra_2_laba(img_in)
        top_similars[img_file] = (deltaE_ciede2000(im1_lab, im2_lab).mean(),
                                  img_in)
    top_similars = list(sorted(top_similars.items(),
                               key=lambda item: item[1][0]))
    top_5_imgs = [top_item[1][1] for top_item in top_similars[:top_count]]
    # print("TOP 5 SIMILAR IMAGES BY LAB: ", top_5_imgs)
    return plot_finded_imgs([main_img] + top_5_imgs)


def lab_similar_finder(init_img):
    """
    Функция, подготавливающая все к процессу поиска похожих на переданное
    изображению изображений из имеющейся директории.

    :param init_img: bytes формат изображения.
    :return: np.ndarray формат коллажа из комплементарных изображений.
    """
    logger.info("Started searching similar images for init image!")
    init_image = cv2.imdecode(np.frombuffer(init_img, np.uint8),
                              cv2.IMREAD_UNCHANGED)
    logger.info("Successfully ended searching similar images for init image!")
    return get_top_similar_imgs(init_image, os.getenv("SAVE_HIGHLIGHTED_DIR"))
