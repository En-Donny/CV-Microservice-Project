import cv2
import numpy as np
from PIL import Image
from PIL.ImageDraw import Draw


def grid_plot(init_image, other_img_pathes):
    """
    Функция, позволяющая вывести сетку из изображений, которые явяляются
    результатами поисков по изображению и по тексту. Формирует сетку изображений
    в формате np.array.

    :param init_image: Первое изображение для отрисовки в сетке.
    :param other_img_pathes: Полные пути для открытия файлов всех найденных
        изображений.
    :return: Сетка-результат поиска изображений.
    """
    image_grid = Image.new("RGB", (1000, 1000))
    main_image = Image.fromarray(init_image)
    main_image = main_image.resize((200, 200))
    image_draw = Draw(main_image)
    image_draw.rectangle([(0, 0), (194, 194)], outline="red", width=6)
    image_grid.paste(main_image, ((0, 0)))
    for j, path in enumerate(other_img_pathes):
        search_image = cv2.imread(path)
        search_image = Image.fromarray(search_image)
        search_image = search_image.resize((200, 200))
        image_grid.paste(search_image, ((200 * ((j + 1) % 5),
                                         200 * ((j + 1) // 5))))
    return np.array(image_grid)
