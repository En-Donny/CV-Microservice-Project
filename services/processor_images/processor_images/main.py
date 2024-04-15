import os

import uvicorn
from fastapi import FastAPI, Response
import cv2
from io import BytesIO
from processor_images.img_processing import prepare_highlighter, prepare_merger

app = FastAPI()


@app.get("/highlight_all_imgs")
async def highlight_all():
    await prepare_highlighter()
    return {"ALL IMAGES HIGHLIGHTED"}


@app.post("/highlight_particular_img")
async def highlight_particular_img(body: dict):
    res = await prepare_highlighter(body)
    img_rgb = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
    _, buffer = cv2.imencode(".png", img_rgb)
    return Response(content=BytesIO(bytes(buffer)).getvalue(),
                    media_type="image/png")


@app.post("/merge_two_images")
async def merge_imgs(body: dict):
    res = await prepare_merger(body)
    img_rgb = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
    _, buffer = cv2.imencode(".png", img_rgb)
    return Response(content=BytesIO(bytes(buffer)).getvalue(),
                    media_type="image/png")


def start():
    """Launched with `poetry run start`"""
    uvicorn.run(
        "processor_images.main:app",
        host=os.getenv("SCRAPER_HOST"),
        port=int(os.getenv("SCRAPER_PORT")),
        reload=True
    )
