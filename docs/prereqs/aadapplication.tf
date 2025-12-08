resource "time_rotating" "expiration" {
  rotation_days = 180
}

resource "random_uuid" "uuid_application_app_role" {}

resource "azuread_application" "application" {
  count = var.entra_application_enabled ? 1 : 0
  
  display_name = local.application_name
  description  = "Azure AD OAuth Bot App"

  notes                         = "Some Notes"
  oauth2_post_response_required = false
  owners                        = [data.azuread_client_config.current.object_id]
  prevent_duplicate_names       = true
  sign_in_audience              = "AzureADMyOrg"

  password {
    display_name = "bot-login"
    start_date   = time_rotating.expiration.id
    end_date     = timeadd(time_rotating.expiration.id, "4320h")
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
}

resource "azuread_service_principal" "service_principal" {
  count = var.entra_application_enabled ? 1 : 0

  client_id    = one(azuread_application.application[*].client_id)
  use_existing = true

  account_enabled              = true
  alternative_names            = []
  app_role_assignment_required = false
  description                  = "Service Principal for AAD Auth."
  notes                        = "Service Principal for AAD in teh Bot Frameowork."
  owners = [
    data.azuread_client_config.current.object_id
  ]
}
