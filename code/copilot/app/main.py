from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.api.v1.router import api_v1_router
from app.copilot.copilot import connection_manager
from app.core.settings import settings
from app.logs import setup_opentelemetry
from app.auth import get_scopes_as_dict, auth_settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from microsoft_agents.hosting.fastapi import JwtAuthorizationMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Gracefully start the application before the server reports readiness.
    """
    # Configure open telemetry
    setup_opentelemetry()

    # Configure auth
    await auth_settings.openid_config.load_config()

    yield


def get_app() -> FastAPI:
    """
    Setup the Fast API server.

    RETURNS (FastAPI): The FastAPI object to start the server.
    """
    # Create app
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="",
        version=settings.APP_VERSION,
        openapi_url="/openapi.json",
        debug=settings.DEBUG,
        lifespan=lifespan,
        swagger_ui_oauth2_redirect_url='/oauth2-redirect',
        swagger_ui_init_oauth={
            'usePkceWithAuthorizationCodeGrant': True,
            'clientId': settings.CLIENT_ID,
            'scopes': get_scopes_as_dict(),
        },
    )

    # Add middleware
    # app.state.agent_configuration = (
    #     connection_manager.get_default_connection_configuration()
    # )
    # app.add_middleware(JwtAuthorizationMiddleware)
    app.add_middleware(CORSMiddleware,
        allow_origins=[str(origin) for origin in [f"http://{settings.BASE_URL}", f"https://{settings.BASE_URL}"]],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    # Add router
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)

    return app


app = get_app()
