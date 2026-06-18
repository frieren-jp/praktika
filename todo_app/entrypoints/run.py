from pathlib import Path
import sys

import uvicorn
from fastapi import FastAPI

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.archtool_conf.bundle_project import bundle
from app.config import HOST, PORT


def create_app() -> FastAPI:
    app = FastAPI(title="BASIC-2 ToDo API")
    bundle(app)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("entrypoints.run:app", host=HOST, port=PORT, reload=True)
