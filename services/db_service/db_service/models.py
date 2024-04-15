from pydantic import BaseModel


# Класс для запроса вставки в базу данных
class InsertScrappedImgParams(BaseModel):
    img_name: str
    img_hash: str
    img_path: str


# Класс для запроса получения данных из базы
class GetScrappedImgParams(BaseModel):
    img_name: str
