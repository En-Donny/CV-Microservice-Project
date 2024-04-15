import uvicorn
import os
from fastapi import FastAPI

from db_service.models import (
    InsertScrappedImgParams,
    GetScrappedImgParams,
    UpdateScrappedImgParams,
)
from db_service.img_db import IMGDatabase

app = FastAPI()
db = IMGDatabase()


@app.on_event("startup")
async def startup_event():
    conn_str = (f'postgresql://{os.getenv("POSTGRES_USER")}:'
                f'{os.getenv("POSTGRES_PASSWORD")}@'
                f'{os.getenv("DB_CONTAINER_NAME")}:{os.getenv("POSTGRES_PORT")}'
                f'/{os.getenv("POSTGRES_DB")}')
    await db.connect(conn_str)


@app.on_event("shutdown")
async def shutdown_event():
    await db.disconnect()


@app.post("/insert_scrapped_imgs")
async def insert_scrapped_imgs(request: InsertScrappedImgParams):
    res = await db.insert_scrapped_imgs(request.img_name,
                                        request.img_hash,
                                        request.img_path)
    return {"content": res}


@app.post("/get_img")
async def get_scrapped_imgs(request: GetScrappedImgParams):
    res = await db.get_by_filename(request.img_path)
    return res


@app.get("/get_all_not_highlighted")
async def get_all_not_highlighted():
    res = await db.get_all_not_highlighted_imgs()
    return {"answer": res}


@app.post("/update_record")
async def update_record(request: UpdateScrappedImgParams):
    await db.update_one_record(request.id,
                               request.img_name,
                               request.img_hash,
                               request.img_path,
                               request.is_highlighted)
    return {"answer": "success"}


@app.get("/clear")
async def clear():
    res = await db.clear_all()
    return res


def start():
    uvicorn.run(
        "db_service.main:app",
        host=os.getenv("DB_IMG_HOST"),
        port=int(os.getenv("DB_IMG_PORT")),
        reload=True
    )
