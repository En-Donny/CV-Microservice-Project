"""
Файл, перенаправляющий запросы к FastAPI на другие сервисы.
"""

import uvicorn
import os
import aiohttp
from fastapi import FastAPI, Request, Response
from back.logging.logger import get_logger

app = FastAPI()
session: aiohttp.ClientSession
logger = get_logger("BACK")
server_error_code = 500
server_error_text = "Something wrong on the server side!"


async def send_post(request: Request, url_request: str):
    """
    Метод для формирования и отправки POST-запроса.

    :param request: объект запроса.
    :param url_request: url-адрес отправки запроса в формате str.
    :return: Response.
    """
    try:
        async with session.post(
                url_request,
                headers=request.headers,
                data=await request.body()
        ) as resp:
            return Response(status_code=resp.status,
                            headers=resp.headers,
                            content=await resp.content.read())
    except Exception as e:
        logger.error(f"Got error while processing the request! REASON: {e}")
        return Response(status_code=server_error_code,
                        content=server_error_text)


async def send_get(request: Request, url_request: str):
    """
    Метод для формирования и отправки GET-запроса.

    :param request: объект запроса.
    :param url_request: url-адрес отправки запроса в формате str.
    :return: Response.
    """
    try:
        async with session.get(url_request, headers=request.headers) as resp:
            return Response(status_code=resp.status,
                            headers=resp.headers,
                            content=await resp.content.read())
    except Exception as e:
        logger.error(f"Got error while processing the request! REASON: {e}")
        return Response(status_code=server_error_code,
                        content=server_error_text)


@app.on_event("startup")
async def startup_event():
    global session
    session = aiohttp.ClientSession()


@app.on_event("shutdown")
async def shutdown_event():
    global session
    await session.close()


@app.get("/scrape")
async def scrape(request: Request):
    return await send_get(request, os.getenv('SCRAPER_URL'))


@app.post('/hello')
async def hello(request: Request):
    return await send_post(request, os.getenv('GET_ONE_URL'))


@app.get('/clear_all')
async def clear_all(request: Request):
    return await send_get(request, os.getenv('DELETE_URL'))


@app.get('/highlight_all_images')
async def highlight_all_images(request: Request):
    return await send_get(request, os.getenv('PROCESSOR_URL'))


@app.post('/highlight_particular_image')
async def highlight_particular_image(request: Request):
    return await send_post(request, os.getenv('PROCESSOR_ONE_URL'))


@app.post('/merge_imgs')
async def merge_imgs(request: Request):
    return await send_post(request, os.getenv('MERGE_URL'))


@app.post('/find_all_complementary')
async def find_complementary(request: Request):
    return await send_post(request, os.getenv('CV2_IMG_SEARCH_URL_HSV'))


@app.post('/find_all_similar_by_lab')
async def find_all_similar_by_lab(request: Request):
    return await send_post(request, os.getenv('CV2_IMG_SEARCH_URL_LAB'))


@app.get('/get_all_resnet_embeddings')
async def get_all_resnet_embeddings(request: Request):
    return await send_get(request, os.getenv('GET_EMBEDDINGS_RESNET_URL'))


@app.get('/get_all_clip_embeddings')
async def get_all_clip_embeddings(request: Request):
    return await send_get(request, os.getenv('GET_EMBEDDINGS_CLIP_URL'))


@app.post('/get_top_24_resnet_similar')
async def get_top_24_resnet_similar(request: Request):
    return await send_post(request, os.getenv('MODEL_IMG_SEARCH_RESNET_URL'))


@app.post('/get_top_25_clip_similar')
async def get_top_25_clip_similar(request: Request):
    return await send_post(request, os.getenv('MODEL_IMG_SEARCH_CLIP_URL'))


def start():
    uvicorn.run(
        "back.main:app",
        host=os.getenv("BACK_HOST"),
        port=int(os.getenv("BACK_PORT")),
        reload=True
    )
