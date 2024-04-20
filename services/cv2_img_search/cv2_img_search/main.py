import os

import uvicorn
from fastapi import FastAPI, Response, Request, UploadFile, File
import cv2
from io import BytesIO
from cv2_img_search.image_searching_hsv import hsv_complement_finder
from cv2_img_search.image_searching_lab import lab_similar_finder

app = FastAPI()


@app.post('/find_all_complementary')
async def find_all_complementary(image: UploadFile = File(...)):
    res_img = hsv_complement_finder(await image.read())
    _, buffer = cv2.imencode(".png", res_img)
    return Response(content=BytesIO(bytes(buffer)).getvalue(),
                    media_type="image/png")


@app.post('/find_all_similar_by_lab')
async def find_all_similar_by_lab(image: UploadFile = File(...)):
    res_img = lab_similar_finder(await image.read())
    _, buffer = cv2.imencode(".png", res_img)
    return Response(content=BytesIO(bytes(buffer)).getvalue(),
                    media_type="image/png")


def start():
    """Launched with `poetry run start`"""
    uvicorn.run(
        "cv2_img_search.main:app",
        host=os.getenv("CV2_IMG_SEARCH_HOST"),
        port=int(os.getenv("CV2_IMG_SEARCH_PORT")),
        reload=True
    )
