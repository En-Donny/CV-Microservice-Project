"""
Файл, перенаправляющий запросы к FastAPI на другие сервисы.
"""

import uvicorn
import os
import aiohttp
from fastapi import FastAPI, Request

app = FastAPI()
session: aiohttp.ClientSession


@app.on_event("startup")
async def startup_event():
    global session
    session = aiohttp.ClientSession()


@app.on_event("shutdown")
async def shutdown_event():
    global session
    await session.close()


@app.get("/scrape")
async def root():
    async with session.get(os.getenv("SCRAPER_URL")) as data:
        ans = await data.json()
    return ans


@app.post('/hello')
async def hello(request: Request):
    data = await request.json()
    async with session.post(os.getenv('TEST_URL'), json=data) as resp:
        response = await resp.json()
    return {"ans": response}


@app.get('/clear_all')
async def clear_all():
    async with session.get(os.getenv('DELETE_URL')) as resp:
        response = await resp.json()
    return {"ans": response}


def start():
    uvicorn.run(
        "back.main:app",
        host=os.getenv("BACK_HOST"),
        port=int(os.getenv("BACK_PORT")),
        reload=True
    )
