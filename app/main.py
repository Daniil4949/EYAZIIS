import sys
from typing import Optional

import uvicorn
from fastapi import FastAPI

from app.config import setup_config
from app.container import ApplicationContainer
from app.web import build_v1_router


def create_web_app(
    container: Optional[ApplicationContainer] = None,
) -> FastAPI:
    container = container or ApplicationContainer()

    setup_config(container.config)

    app = container.app()
    app.state.container = container

    # Инжекция зависимостей объявленных в контейнере
    container.wire(packages=[sys.modules["app.web"]])

    v1_router = build_v1_router()

    app.include_router(v1_router)
    app.add_event_handler("startup", container.init_resources)
    app.add_event_handler("shutdown", container.shutdown_resources)

    return app


def main() -> None:
    app = create_web_app()
    port = app.state.container.config.server.port()
    uvicorn.run(app, port=port, log_config=None)
