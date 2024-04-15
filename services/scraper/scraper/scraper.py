"""
Файл с описанием функций скрапинга изображений с сайта
https://world.maxmara.com.
"""

import os

import aiohttp
import numpy as np
import cv2
import asyncio
from bs4 import BeautifulSoup

from scraper.logging.logger import get_logger

headers = {
        "content-type": "application/x-www-form-urlencoded",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/119.0.0.0 Safari/537.36")
    }
main_url = os.getenv("MAIN_URL")
cnt = 0
logger = get_logger("SCRAPER")


def make_filename(name: str) -> str:
    """
    Функция для корректировки названий для файлов изображений и записей с
    информацией об этих изображениях в базе данных. Удаляет те символы из строки
    с названием, которые в дальнейшем помешают при обработке этих названий
    моделями.

    :param name: Имя для изображения.
    :return: Скорректированное имя для изображения.
    """
    del_symbols = ['\\', ':', '*', '?', '"', '<', '>', '|']
    for c in del_symbols:
        name = name.replace(c, '')
    name = name.replace("/", "_")
    return ' '.join(name.split())


def dhash(image, hash_size: int = 32) -> int:
    """
    Функция для вычисления перцептивного хэша изображения.

    :param image: Изображение, переведенное в формат numpy.ndarray с помощью
        методов opencv.
    :param hash_size: Параметр уменьшения размера входного изображения.
        Используется в алгоритме получения перцептивного хэша.
    :return: Значение перцептивного хэша переданного изображения.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (hash_size + 1, hash_size))
    diff = resized[:, 1:] > resized[:, :-1]
    return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])


async def async_scrape(start_urls: list[tuple[str, str]]) -> None:
    """
    Асинхронная функция для скачивания изображений по ранее собранным ссылкам.
    По каждой ссылке на изображение в переданном в параметрах списке переходит
    по ссылке, сохраняет файл изображения в ранее указанную папку для
    сохранения, а также вставляет запись с названием изображения, путем до
    расположения файла, вычисленным хэшом изображения и флагом
    предобработки изображения в базу данных.

    :param start_urls: Список кортежей из ссылок на изображения и их текстовые
        имена.
    :return: None
    """
    conn = aiohttp.TCPConnector()
    session = aiohttp.ClientSession(connector=conn, headers=headers)
    _session = aiohttp.ClientSession()
    loop = asyncio.get_event_loop()
    save_dir = os.getenv("SAVE_IMG_DIR")
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    async def parse_url(url, descr):
        global cnt
        nonlocal save_dir
        try:
            logger.info(f"Visiting [{url}]")
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                # Сохранение изображения на диск
                img = await response.content.read()
                img_cv2 = cv2.imdecode(np.frombuffer(img, np.uint8),
                                       cv2.IMREAD_COLOR)
                img_hash = str(dhash(img_cv2))
                cnt += 1
                filepath = f'{save_dir}{cnt}.{descr}.jpg'

                data = {
                    "img_name": descr,
                    "img_hash": img_hash,
                    "img_path": filepath
                }
                async with _session.post(os.getenv("DB_IMG_INSERT_URL"),
                                         json=data) as insert_response:
                    insert_response.raise_for_status()
                    insert_result = await insert_response.json()
                    if int(insert_result['content']) == 0:
                        with open(filepath, 'wb') as out_file:
                            logger.info(f"Image [{descr}] "
                                        f"successfully added to data base")
                            out_file.write(img)
                    else:
                        logger.info(
                            f"Found duplicate key for image [{descr}], skip "
                            f"inserting")
        except Exception as e:
            logger.error(f"Got error while scrapping on [{url}]. REASON: {e}")
            return

    tasks_lst = [loop.create_task(parse_url(url, desc))
                 for url, desc in start_urls]
    await asyncio.wait(tasks_lst)

    await _session.close()
    await session.close()
    await conn.close()


async def prepare_scraper() -> int:
    """
    Асинхронная функция получения списка ссылок на изображения. Проходя по html
    коду страницы с помощью методов BeautifulSoup находит ссылки на внутренние
    страницы сайта, которые содержат сами изображения и их текстовые описания.
    Полученный список ссылок и текстовых описаний изображений далее передается в
    качестве параметра в функцию async_scrape для получения файлов изображений и
    сохранения информации об изображениях в БД.

    :return: Количество соскрапленных с сайта изображений.
    """
    global main_url, headers
    scrape_headers = headers
    scrape_headers["Connection"] = "keep-alive"
    conn = aiohttp.TCPConnector()
    session = aiohttp.ClientSession(connector=conn, headers=scrape_headers)

    list_child_url = [
        "/clothing", "/coats-and-jackets", "/bags-and-shoes", "/accessories"
    ]
    set_of_links = set()

    async def find_links(url_child):
        async with session.get(url=main_url + url_child) as resp:
            text = await resp.content.read()
            soup = BeautifulSoup(text, "lxml")
            tags_to_child_pages = soup.find_all(
                "a",
                {"class": "cta-secondary"}
            )
            for tag in tags_to_child_pages:
                curr_link_domain = main_url + tag["href"]
                for num_page in range(1, int(os.getenv("END_RANGE_SCRAPER"))):
                    async with session.get(
                            url=(curr_link_domain +
                                 "?focus=true&isRefineSearch=true&page="
                                 f"{num_page}&q=%3AtopRated&resetQuery=true&"
                                 "save=false&sort=topRated")
                    ) as child_page:
                        child_page_soup = BeautifulSoup(
                            await child_page.content.read(),
                            "lxml"
                        )
                        tags_to_child_pages_intro = child_page_soup.find_all(
                            "div",
                            {"class": "image-wrapper"}
                        )
                        for wrapper in tags_to_child_pages_intro:
                            cur_img = wrapper.find(
                                "img",
                                {"class": "media lazyload"}
                            )
                            cur_link = cur_img["data-src"]
                            cur_label = cur_img["alt"].split(" - ")[0]
                            set_of_links.add((cur_link, cur_label))

    loop = asyncio.get_event_loop()
    tasks_lst = [loop.create_task(find_links(url)) for url in list_child_url]

    await asyncio.wait(tasks_lst)

    list_of_links = []
    for pair in set_of_links:
        list_of_links.append((pair[0], make_filename(pair[1])))
    logger.info("!!! Start downloading images !!!")
    await session.close()
    await conn.close()
    await async_scrape(list_of_links)

    return len(list_of_links)
