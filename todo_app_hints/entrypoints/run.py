# ПОДСКАЗКА: это точка входа приложения.
# Если на ревью спрашивают "откуда стартует проект", начинай отсюда.

# Path нужен, чтобы вычислить корень проекта.
from pathlib import Path

# sys нужен, чтобы добавить корень проекта в sys.path.
# Это помогает Python находить пакет app при запуске из entrypoints.
import sys

# uvicorn - ASGI-сервер, который запускает FastAPI-приложение.
import uvicorn

# FastAPI - основной web framework.
from fastapi import FastAPI

# ROOT указывает на папку todo_app.
ROOT = Path(__file__).resolve().parents[1]

# Если корня проекта еще нет в sys.path, добавляем.
# Без этого импорт app.archtool_conf.bundle_project может не найтись.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# bundle - функция, которая собирает DI, БД и роуты.
from app.archtool_conf.bundle_project import bundle

# HOST и PORT вынесены в config.py, чтобы настройки не были зашиты в код запуска.
from app.config import HOST, PORT


# ПОДСКАЗКА: create_app() - фабрика FastAPI-приложения.
# Такой формат удобен для uvicorn, тестов и повторного использования.
def create_app() -> FastAPI:
    # Создаем объект FastAPI.
    app = FastAPI(title="BASIC-2 ToDo API")

    # Собираем приложение: DI, SQLAlchemy, роутеры.
    bundle(app)

    # Возвращаем готовое приложение.
    return app


# app - объект, который uvicorn импортирует как entrypoints.run:app.
app = create_app()


# Этот блок срабатывает только при запуске файла напрямую:
# python entrypoints/run.py
if __name__ == "__main__":
    # Запускаем uvicorn. reload=True удобен при разработке.
    uvicorn.run("entrypoints.run:app", host=HOST, port=PORT, reload=True)
