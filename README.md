# Микросервисное приложение на основе проекта по компьютерному зрению

Этот проект, организованный в микросервисной архитектуре, реализующий некоторые
методы из области компьютерного зрения на основе заданий из учебной дисциплины
"Компьютерное зрение". Саратов, 2024 год.

## Функционал проекта

В данном проекте реализованы следующие функции:
- скрапинг изображений и их сохранение с учетом уникальности,
- удаление фона с изображений,
- склейка изображений,
- поиск изображений по входному изображению,
- поиск изображений по текстовому запросу.

## Требования к запуску проекта

Необходимо склонировать данный репозиторий к себе на локальную машину, создать
файл `.env` внутри него и заполнить его в соответсвтии с файлом `.env.example`.
Также убедитесь, что у Вас установлен и запущен Docker.

## Запуск

Проект можно запустить с помощью следующих команд:
- `make run` — собирает все описанные в файле docker-compose образы и запускает
  все Докер-контейнеры;
- `make delete-all` — останавливает все контейнеры и удаляет все образы;
- `make clean-local` — останавливает все контейнеры и удаляет только локально
  собранные образы.
