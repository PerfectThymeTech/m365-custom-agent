from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer
from app.core.settings import settings


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
    )

    return auth_settings


auth_settings = get_auth_settings()
