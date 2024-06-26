# Сервис back
Данный сервис посредством запросов организует сообщение со всеми остальными
сервисами, которые уже, в свою очередь, реализуют основной функционал проекта.
API проекта разворачивается по следующему адресу: http://localhost:8004

## API
На данный момент реализованы следующие запросы к данному сервису:
- `/scrape`: GET запрос. Запускает поиск ссылок на изображения и сохранение всех
  найденных изображений в локальные директории и в базу данных;


- `/hello`: POST запрос. Запускает функцию получения информации об изображении
  из базы данных. Необходимо в качестве тела запроса передавать JSON вида:
  ```
  {'img_path': 'путь_до_изображения'}
  ```


- `/clear_all`: GET запрос. Производит очистку содержимого базы данных;


- `/highlight_all_images`: GET запрос. Производит удаление фона со всех ранее 
  соскрапленных изображений.


- `/highlight_particular_image`: POST запрос. Производит удаление фона с
  изображения, путь до которого был передан в теле запроса. Необходимо в
  качестве тела запроса передавать JSON вида:
  ```
  {'img_path': 'путь_до_изображения'}
  ```
  
- `/merge_imgs`: POST запрос. Производит склейку двух изображений по алгоритму
  пирамиды Лапласа. Необходимо в качестве тела запроса передавать JSON вида:
  ```
  {
      "img_path_1": "путь_до_изображения_1", 
      "img_path_2": "путь_до_изображения_2"
  }
  ```

- `/find_all_complementary`: POST запрос. Производит поиск комлпементарных по
  модели HSV изображений к переданному в запросе. Запрос (form-data) передается
  со следующим телом:
  1. В качестве ключа указывается имя "image";
  2. В качестве значения передается .png файл.
  
  Примечание: для лучшего качества результата необходимо передавать изображение
  с удаленным фоном.


- `/find_all_similar_by_lab`: POST запрос. Производит поиск похожих по
  модели LAB изображений к переданному в запросе. Метрикой похожести в данном 
  алгоритме является CIEDE2000. Запрос (form-data) передается со следующим 
  телом:
  1. В качестве ключа указывается имя "image";
  2. В качестве значения передается .png файл.
  
  Примечание: для лучшего качества результата необходимо передавать изображение
  с удаленным фоном.


- `/get_all_resnet_embeddings`: GET запрос. Производит вычисление эмбеддингов
  всех изображений в БД, для которых еще не проводились вычисления, с помощью 
  модели ResNet34. Результаты записываются в таблицу в столбец 
  'embedding_resnet'.


- `/get_all_clip_embeddings`: GET запрос. Производит вычисление эмбеддингов
  всех изображений в БД, для которых еще не проводились вычисления, с помощью 
  модели CLIP. Результаты записываются в таблицу в столбец 'embedding_clip'.


- `/get_top_24_resnet_similar`: POST запрос. Производит поиск ТОП-24 наиболее 
  соответстующих переданному в запросе изображению среди записей в базе данных.
  Сравнение схожести проводится с использованием косинусной меры по эмбеддингам,
  вычисленным моделью ResNet34. Запрос (form-data) передается со следующим 
  телом:
  1. В качестве ключа указывается имя "image";
  2. В качестве значения передается изображение в формате `.jpg` или `.png`.
  Изображение, переданное в запросе, подставляется в начало коллажа-результата и
  обводится в рамку.

- `/get_top_25_clip_similar`: POST запрос. Производит поиск ТОП-25 изображений,
  наиболее соответстующих переданному в запросе тексту. Сравнение схожести 
  проводится с использованием косинусной меры по эмбеддингам, вычисленным 
  моделью CLIP. Необходимо в качестве тела запроса передавать JSON вида:
  ```
  {
    "text_query": "текст запроса"
  }
  ```