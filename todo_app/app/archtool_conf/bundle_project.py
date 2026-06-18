from importlib import import_module
from pathlib import Path

from archtool.dependency_injector import DependencyInjector
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from web_fractal.building_utils import import_all_models, initialize_controllers_api
from web_fractal.db import Base

from app.archtool_conf.custom_layers import APPS, app_layers
from app.config import DATABASE_URL


ROOT = Path(__file__).resolve().parents[2]


def _import_all_models_compat() -> None:
    try:
        import_all_models(Base)
    except TypeError:
        # web_fractal 0.0.1 has a path expression that fails on Windows/WSL.
        # The fallback keeps the same intent: import every AppModule's models.py
        # before Base.metadata.create_all().
        for app_module in APPS:
            try:
                import_module(f"{app_module.import_path}.models")
            except ModuleNotFoundError:
                continue


def bundle(app: FastAPI) -> DependencyInjector:
    injector = DependencyInjector(
        modules_list=APPS,
        layers=app_layers,
        project_root=ROOT,
    )

    engine = create_async_engine(DATABASE_URL, echo=False)
    session_maker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    injector.register(key=AsyncEngine, value=engine, inject_into=False)
    injector.register(key=async_sessionmaker, value=session_maker, inject_into=False)

    _import_all_models_compat()
    injector.inject()

    # Compatibility with web_fractal 0.0.1, which reads injector._dependencies.
    if not hasattr(injector, "_dependencies"):
        injector._dependencies = injector.dependencies

    app.state.injector = injector
    initialize_controllers_api(injector=injector, app=app)

    @app.on_event("startup")
    async def create_tables() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    return injector
