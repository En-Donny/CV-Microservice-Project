import os

import numpy as np
import cv2
from cv2_img_search.logging.logger import get_logger
from cv2_img_search.collage_maker import plot_finded_imgs

logger = get_logger("HSV_SEARCHER_IMAGES")


def bgra_2_hsva(image):
    """
    Метод для перевода изображения из BGRa-формата в HSVa-формат. Переданное
    изображение не меняется.

    :param image: Изображение, над которым необходимо произвести указанные
        в описании метода действия.
    :return: Возвращает HSVa-формат изображения и кортеж из 2-х размерностей
        обработанного изображения.
    """
    base_sizes = image.shape
    resized_img = cv2.resize(image, (int(os.getenv("MEAN_WIDTH")),
                                     int(os.getenv("MEAN_HEIGHT"))))
    hsv_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2HSV)
    result = resized_img.copy()
    result[:, :, :3] = hsv_img
    return result, (base_sizes[1], base_sizes[0])


def get_all_complementary(init_img, interval_len, confidence_coef=0.75):
    """
    Функция, позволяющая по переданному в качестве параметра изображению искать
    среди всех остальных обработанных изображений комплементарные по палитре
    HSV. Сохраняет все комплементарные изображения в список, который потом
    передается в функцию plot_finded_imgs для создания
    коллажа из комплементарных изображений.

    :param init_img: np.ndarray формат входного изображения.
    :param interval_len: Диапазон значений для учета погрешности при поиске
        комплементарных изображений.
    :param confidence_coef: Коэффициент, необходимый при учете количества схожих
        пикселей.
    :return: np.ndarray формат коллажа из комплементарных изображений.
    """
    dir = os.getenv("SAVE_HIGHLIGHTED_DIR")
    list_complementary_files = [init_img]
    hsv_full, base_size = bgra_2_hsva(init_img)
    # Находим H компоненту картинки
    h_img_1 = hsv_full[:, :, 0].astype(np.uint16) * 2
    # Маска нужна будет дальше при нахождении комплементарного цвета картинки,
    # чтобы не учитывать нули
    mask = np.where(h_img_1 == 0, 0, 1)
    h_complement = ((180 + h_img_1) % 360) * mask
    # Значение для границ диапазона поиска комплементарных картинок
    # Находим левую границу для поиска
    comp_minus_tol = (h_complement - interval_len) % 360
    # Находим правую границу для поиска
    comp_plus_tol = (h_complement + interval_len) % 360
    # Сохраняем количество пикселей в картинке
    h_1_cnt_px = h_img_1.shape[0] * h_img_1.shape[1]
    # Проходимся вложенным циклом по всем другим картинкам
    for img_file_2 in os.listdir(dir):
        img_sec = cv2.imread(dir + img_file_2, cv2.IMREAD_UNCHANGED)
        # Для каждой картинки находим H компоненту
        hsv_2_full, base_size = bgra_2_hsva(img_sec)
        h_img_2 = hsv_2_full[:, :, 0].astype(np.uint16) * 2
        # Если количество пикселей текущей H компоненты, которые уложились
        # в диапазон от нижней границы до верхней границы больше, чем 0.75
        # от общего количества пикселей ==> это наша комплементарная
        # картинка
        comparison = np.where(comp_minus_tol <= comp_plus_tol,
                              ((comp_minus_tol <= h_img_2) &
                               (h_img_2 <= comp_plus_tol)),
                              ((comp_minus_tol <= h_img_2) |
                               (h_img_2 <= comp_plus_tol))
                              )
        if comparison.sum() >= confidence_coef * h_1_cnt_px:
            list_complementary_files.append(img_sec)
    return plot_finded_imgs(list_complementary_files)


def hsv_complement_finder(main_img):
    """
    Функция, подготавливающая все к процессу поиска комплементарных переданному
    изображению изображений из имеющейся директории.

    :param main_img: bytes формат изображения.
    :return: np.ndarray формат коллажа из комплементарных изображений.
    """
    logger.info("Started searching complementary images for init image!")
    init_image = cv2.imdecode(np.frombuffer(main_img, np.uint8),
                              cv2.IMREAD_UNCHANGED)
    logger.info("Successfully ended searching complementary images for init "
                "image!")
    return get_all_complementary(init_image, 40, 0.6)
