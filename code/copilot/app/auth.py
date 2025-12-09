from app.core.settings import settings
from app.logs import setup_logging
from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer
from fastapi_azure_auth.exceptions import ForbiddenHttp, UnauthorizedHttp
from fastapi_azure_auth.user import User
from fastapi import Depends

logger = setup_logging(__name__)


def get_scopes_as_dict() -> dict[str, str]:
    # Create result dict
    result_dict = {}

    # Iterate through scopes
    for scope in settings.SCOPES:
        # Create key and value
        scope_key = scope
        scope_value = scope.split("//")[-1].split("/")[-1]

        # Add scope to result dict
        result_dict[scope_key] = scope_value

    return result_dict


def get_auth_settings() -> SingleTenantAzureAuthorizationCodeBearer:
    # Get scopes as dict
    scopes_as_dict = get_scopes_as_dict()

    # Create auth settings and return
    auth_settings = SingleTenantAzureAuthorizationCodeBearer(
        app_client_id=settings.CLIENT_ID,
        tenant_id=settings.TENANT_ID,
        auto_error=True,
        scopes=scopes_as_dict,
        leeway=0,
        allow_guest_users=False,
        openid_config_use_app_id=True,
        # openapi_authorization_url="https://login.microsoftonline.com/d6d49420-f39b-4df7-a1dc-d59a935871db/oauth2/v2.0/authorize" # "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize",
        # openapi_token_url="https://login.microsoftonline.com/d6d49420-f39b-4df7-a1dc-d59a935871db/oauth2/v2.0/token"
    )

    return auth_settings


auth_settings = get_auth_settings()


async def validate_is_valid_user(user: User = Depends(auth_settings)) -> None:
    """
    Validate that the user is a valid user.
    
    :param user: The user auth settings.
    :type user: User
    """
    # logger.info(f"Validating user: {user.upn}")
    # logger.info(f"User roles: {user.roles}")
    # logger.info(f"User groups: {user.groups}")
    # logger.info(f"User tenant id: {user.tid}")
    # logger.info(f"Expected tenant id: {settings.TENANT_ID}")
    # logger.info(f"User object id: {user.oid}")
    # logger.info(f"User app id: {user.appid}")
    # logger.info(f"User access token: {user.access_token}")
    # logger.info(f"User auth audience: {user.aud}")
    # logger.info(f"User auth claims: {user.claims}")
    # logger.info(f"User json: {user.model_dump_json()}")

    if user.tid != settings.TENANT_ID or user.is_guest:
        raise ForbiddenHttp('User is part of the wrong tenant or just a guest user.')
