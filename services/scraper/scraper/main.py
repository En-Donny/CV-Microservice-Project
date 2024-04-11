import os

import uvicorn
from fastapi import FastAPI

from scraper.scraper import prepare_scraper

app = FastAPI()


@app.get("/scrape")
async def scrape():
    return {"answer": f"Scraped {await prepare_scraper()} pages!"}


def start():
    """Launched with `poetry run start`"""
    uvicorn.run(
        "scraper.main:app",
        host=os.getenv("SCRAPER_HOST"),
        port=int(os.getenv("SCRAPER_PORT")),
        reload=True
    )
