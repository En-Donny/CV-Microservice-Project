# Сервис для поиска по изображению
Данный сервис реализует функционал методов поиска комплементарных и похожих 
примеров для входного изображения. 
Использует следующие исполняемые файлы:
- `main.py`: реализует функционал обращение к методам поиска изображений через
    API;
- `image_searching_hsv.py`: в этом файле реализован метод поиска комлпементарных 
    по HSV-модели изображений к переданному изображению в запросе;
- `image_searching_lab.py`: в этом файле реализован метод поиска похожих по 
    модели LAB изображений к переданному изображению в запросе;
- `collage_maker.py`: в этом файле реализован метод склейки в коллаж всех 
    найденных в вышеописанных алгоритмах изображений в одно большое изображение
    для возврата пользователю в качестве ответа на его запрос.