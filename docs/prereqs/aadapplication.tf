resource "time_rotating" "expiration" {
  count = var.entra_application_enabled ? 1 : 0

  rotation_days = 180
}

resource "random_uuid" "uuid_application_api_oauth2_permission_scope_id" {}

resource "azuread_application" "application" {
  count = var.entra_application_enabled ? 1 : 0

  display_name = local.application_name
  description  = "Azure AD OAuth Bot App"

  notes                         = "Azure AD OAuth Bot App"
  oauth2_post_response_required = false
  owners                        = [data.azuread_client_config.current.object_id]
  prevent_duplicate_names       = true
  sign_in_audience              = "AzureADMyOrg"

  password {
    display_name = "bot-login"
    start_date   = one(time_rotating.expiration[*].id)
    end_date     = timeadd(one(time_rotating.expiration[*].id), "4320h")
  }
  api {
    mapped_claims_enabled          = false
    requested_access_token_version = 2

    oauth2_permission_scope {
      admin_consent_description  = "Teams can call the app's web APIs as the current user."
      admin_consent_display_name = "Teams can access user profile"
      enabled                    = true
      id                         = random_uuid.uuid_application_api_oauth2_permission_scope_id.result
      type                       = "User"
      user_consent_description   = "Teams can access the user profile and make requests on behalf of the user."
      user_consent_display_name  = "Teams can access user profile"
      value                      = "access_as_user"
    }
  }
  required_resource_access {
    resource_app_id = "00000003-0000-0000-c000-000000000000" # Microsoft Graph
    resource_access {
      id   = "37f7f235-527c-4136-accd-4a02d197296e" # openid
      type = "Scope"
    }
    resource_access {
      id   = "14dad69e-099b-42c9-810b-d002981feec1" # profile
      type = "Scope"
    }
    resource_access {
      id   = "e1fe6dd8-ba31-4d61-89e7-88639da4683d" # User.Read
      type = "Scope"
    }
    resource_access {
      id   = "b340eb25-3456-403f-be2f-af7a0d370277" # User.ReadBasic.All
      type = "Scope"
    }
  }
  web {
    redirect_uris = [
      local.redirect_uris[var.data_residency],
      # "https://login.microsoftonline.com",
    ]
  }

  lifecycle {
    ignore_changes = [
      identifier_uris
    ]
  }
}

resource "azuread_application_identifier_uri" "application_identifier_uri" {
  count = var.entra_application_enabled ? 1 : 0

  application_id = one(azuread_application.application[*].id)

  identifier_uri = "api://botid-${one(azuread_application.application[*].client_id)}"
}

resource "azuread_application_pre_authorized" "application_pre_authorized" {
  for_each = var.entra_application_enabled ? local.application_known_client_applications : {}

  application_id       = one(azuread_application.application[*].id)
  authorized_client_id = each.value

  permission_ids = [random_uuid.uuid_application_api_oauth2_permission_scope_id.result]

  depends_on = [
    azuread_application_identifier_uri.application_identifier_uri,
  ]
}

resource "azuread_service_principal" "service_principal" {
  count = var.entra_application_enabled ? 1 : 0

  client_id    = one(azuread_application.application[*].client_id)
  use_existing = true

  account_enabled              = true
  alternative_names            = []
  app_role_assignment_required = false
  description                  = "Service Principal for AAD Auth."
  notes                        = "Service Principal for AAD in the Bot Framework."
  owners = [
    data.azuread_client_config.current.object_id
  ]
}
