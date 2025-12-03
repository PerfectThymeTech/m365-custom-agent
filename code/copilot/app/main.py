from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.api.v1.router import api_v1_router
from app.core.settings import settings
from app.logs import setup_opentelemetry
from fastapi import FastAPI
from microsoft_agents.hosting.fastapi import JwtAuthorizationMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Gracefully start the application before the server reports readiness.
    """
    # Configure open telemetry
    setup_opentelemetry()

    yield


def get_app() -> FastAPI:
    """
    Setup the Fast API server.

    RETURNS (FastAPI): The FastAPI object to start the server.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="",
        version=settings.APP_VERSION,
        openapi_url="/openapi.json",
        debug=settings.DEBUG,
        lifespan=lifespan,
        # middleware=[JwtAuthorizationMiddleware],
    )
    # app.add_middleware(JwtAuthorizationMiddleware)
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)
    return app


app = get_app()
