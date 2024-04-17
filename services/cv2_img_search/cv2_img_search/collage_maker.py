import os

import numpy as np
import cv2


def plot_finded_imgs(list_of_complementary: list[np.ndarray]) -> np.ndarray:
    """
    Функция, позволяющая склеить в коллаж изображения из списка, полученного
    из методов поиска по изображению: по модели HSV или LAB.

    :param list_of_complementary: Список из изображений, которые необходимо
        объединить в коллаж.
    :return: Итоговый коллаж из изображений в формате np.ndarray.
    """
    montage = None
    cnt = 0
    plot_size = int(os.getenv("PLOT_SIZE"))
    for p in list_of_complementary[:10]:
        image = cv2.resize(p, (plot_size, plot_size))
        if montage is None:
            montage = image
        else:
            montage = np.concatenate([montage, image], axis=1)
        cnt += 1
    return montage
