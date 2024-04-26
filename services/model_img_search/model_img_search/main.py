import os

import uvicorn
from fastapi import FastAPI, Response, Request, UploadFile, File
import cv2
from io import BytesIO
from model_img_search.resnet_img_search import (prepare_resnet_search,
                                                get_top_resnet_similar)
import model_img_search.clip_img_search as clip_model_file

app = FastAPI()


@app.get('/get_all_resnet_embeddings')
async def get_all_resnet_embeddings():
    res = await prepare_resnet_search()
    return Response(content=res)


@app.get('/get_all_clip_embeddings')
async def get_all_clip_embeddings():
    res = await clip_model_file.prepare_clip_search()
    return Response(content=res)


@app.post('/find_all_similar_resnet')
async def find_all_similar_resnet(image: UploadFile = File(...)):
    res_img = await get_top_resnet_similar(await image.read())
    _, buffer = cv2.imencode(".png", res_img)
    return Response(content=BytesIO(bytes(buffer)).getvalue(),
                    media_type="image/png")


@app.post('/find_all_similar_clip')
async def find_all_similar_clip(request: Request):
    res_img = await clip_model_file.get_top_clip_similar(await request.json())
    _, buffer = cv2.imencode(".png", res_img)
    return Response(content=BytesIO(bytes(buffer)).getvalue(),
                    media_type="image/png")


def start():
    """Launched with `poetry run start`"""
    uvicorn.run(
        "model_img_search.main:app",
        host=os.getenv("MODEL_IMG_SEARCH_HOST"),
        port=int(os.getenv("MODEL_IMG_SEARCH_PORT")),
        reload=True
    )
