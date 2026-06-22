# ПОДСКАЗКА: этот файл - "сборочный цех" приложения.
# Здесь FastAPI связывается с archtool, web_fractal и SQLAlchemy.
# На ревью этот файл важно объяснить целиком: от создания DI-контейнера
# до регистрации роутеров и создания таблиц в базе.

# Блок импортов стандартной библиотеки.
# import_module нужен для fallback-импорта models.py, если import_all_models()
# из web_fractal падает на текущей версии пакета.
from importlib import import_module

# Path нужен, чтобы вычислить корень проекта и передать его в archtool.
from pathlib import Path

# DependencyInjector - главный объект archtool, который находит реализации
# интерфейсов и внедряет зависимости по аннотациям.
from archtool.dependency_injector import DependencyInjector

# FastAPI нужен только для типа аргумента app в функции bundle().
from fastapi import FastAPI

# SQLAlchemy async-инструменты:
# AsyncEngine - тип engine;
# AsyncSession - тип сессии;
# async_sessionmaker - фабрика сессий;
# create_async_engine - создание async engine.
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

# import_all_models импортирует ORM-модели, чтобы Base.metadata видел таблицы.
# initialize_controllers_api находит HTTP-контроллеры в DI и подключает их router к FastAPI.
from web_fractal.building_utils import import_all_models, initialize_controllers_api

# Base - общий DeclarativeBase для всех SQLAlchemy-моделей.
from web_fractal.db import Base

# APPS - список bounded context модулей: users, todos.
# app_layers - список слоев archtool, которые нужно использовать при сборке.
from app.archtool_conf.custom_layers import APPS, app_layers

# DATABASE_URL - строка подключения к базе SQLite.
from app.config import DATABASE_URL


# ПОДСКАЗКА: ROOT - корень проекта todo_app.
# archtool использует этот путь, чтобы корректно находить app.users, app.todos и т.д.
ROOT = Path(__file__).resolve().parents[2]


# ПОДСКАЗКА: этот блок нужен из-за несовместимости/бага web_fractal 0.0.1.
# Основная идея простая: до create_all() нужно импортировать models.py всех модулей.
def _import_all_models_compat() -> None:
    # Сначала пробуем официальный helper из web_fractal.
    try:
        import_all_models(Base)
    # Если helper падает на работе с путями, делаем то же самое вручную.
    except TypeError:
        # Перебираем AppModule("app.users"), AppModule("app.todos").
        for app_module in APPS:
            try:
                # Импортируем app.users.models или app.todos.models.
                # После импорта классы UserORM/TodoORM регистрируются в Base.metadata.
                import_module(f"{app_module.import_path}.models")
            except ModuleNotFoundError:
                # Если у какого-то модуля нет models.py, просто пропускаем.
                continue


# ПОДСКАЗКА: bundle() вызывается из entrypoints/run.py.
# Эта функция полностью собирает приложение: БД, DI, роуты.
def bundle(app: FastAPI) -> DependencyInjector:
    # Создаем DI-контейнер archtool.
    injector = DependencyInjector(
        # modules_list говорит, какие bounded context нужно сканировать.
        modules_list=APPS,
        # layers явно включает 4 слоя: Presentation, Application, Domain, Infrastructure.
        layers=app_layers,
        # project_root помогает archtool правильно резолвить Python-импорты.
        project_root=ROOT,
    )

    # Создаем async SQLAlchemy engine по DATABASE_URL.
    engine = create_async_engine(DATABASE_URL, echo=False)

    # Создаем фабрику async-сессий.
    # Репозитории не создают ее сами: она будет внедрена через archtool.
    session_maker = async_sessionmaker(
        # bind указывает, через какой engine работать с БД.
        bind=engine,
        # class_ говорит, что фабрика создает AsyncSession.
        class_=AsyncSession,
        # expire_on_commit=False позволяет читать поля ORM-объекта после commit.
        expire_on_commit=False,
    )

    # Регистрируем engine вручную, потому что archtool не может сам создать внешний ресурс.
    injector.register(key=AsyncEngine, value=engine, inject_into=False)

    # Регистрируем session_maker вручную.
    # Потом archtool увидит в репозиториях строку session_maker: async_sessionmaker
    # и подставит туда этот объект.
    injector.register(key=async_sessionmaker, value=session_maker, inject_into=False)

    # Импортируем ORM-модели до создания таблиц.
    _import_all_models_compat()

    # Главный запуск archtool:
    # Pass 1 - найти интерфейсы и реализации;
    # проверка слоев;
    # Pass 2 - внедрить зависимости по аннотациям.
    injector.inject()

    # ПОДСКАЗКА: compatibility bridge для web_fractal 0.0.1.
    # web_fractal ищет приватное поле _dependencies, а archtool 2.1.1 хранит dependencies.
    if not hasattr(injector, "_dependencies"):
        injector._dependencies = injector.dependencies

    # Сохраняем injector в состоянии FastAPI.
    # Это удобно, если потом нужно достать зависимости из app.state.injector.
    app.state.injector = injector

    # Находит все контроллеры, вызывает init_http_routes() и подключает router к FastAPI.
    initialize_controllers_api(injector=injector, app=app)

    # Startup hook FastAPI.
    # Он выполняется при запуске приложения и создает таблицы в SQLite.
    @app.on_event("startup")
    async def create_tables() -> None:
        # Открываем соединение с БД в транзакции.
        async with engine.begin() as conn:
            # SQLAlchemy create_all синхронный, поэтому запускаем через run_sync.
            await conn.run_sync(Base.metadata.create_all)

    # Возвращаем injector, чтобы при необходимости его можно было использовать в тестах.
    return injector
