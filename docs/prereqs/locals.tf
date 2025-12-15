locals {
  # Naming locals
  prefix = "${lower(var.prefix)}-${var.environment}"
  resource_providers_to_register = [
    "Microsoft.Authorization",
    "Microsoft.OperationalInsights",
    "microsoft.insights",
    "Microsoft.Network",
    "Microsoft.Resources",
  ]

  # AAD App locals
  application_name = "${local.prefix}-bot-oauth"
  redirect_uris = {
    none   = "https://token.botframework.com/.auth/web/redirect"
    europe = "https://europe.token.botframework.com/.auth/web/redirect"
    us     = "https://unitedstates.token.botframework.com/.auth/web/redirect"
    india  = "https://india.token.botframework.com/.auth/web/redirect"
    gov    = "https://token.botframework.azure.us/.auth/web/redirect"
  }
  application_known_client_applications = {
    teams_mobile_and_desktop             = "1fec8e78-bce4-4aaf-ab1b-5451cc387264", # Teams mobile or desktop application
    teams_web                            = "5e3ce6c0-2b1f-4285-8d4b-75ee78787346", # Teams web application
    microsoft_365_web                    = "4765445b-32c6-49b0-83e6-1d93765276ca", # Microsoft 365 web application
    microsoft_365_desktop                = "0ec893e0-5785-4de6-99da-4ed124e5296c", # Microsoft 365 desktop application
    microsoft_365_mobile_outlook_desktop = "d3590ed6-52b3-4102-aeff-aad2292ab01c", # Microsoft 365 mobile application/Outlook desktop application
    outlook_web                          = "bc59ab01-8403-45c6-8796-ac3ef710b3e3", # Outlook web application
    outlook_mobile                       = "27922004-5251-4030-b22d-91ecd9a37ea4", # Outlook mobile application
  }
  application_client_id = var.entra_application_enabled ? one(azuread_service_principal.service_principal[*].client_id) : "<your-client-id>"
  application_password  = var.entra_application_enabled ? tolist(one(azuread_application.application[*].password)).0.value : "<your-client-secret>"

  # DNS variables
  private_dns_zone_names = {
    vault                    = "privatelink.vaultcore.azure.net",
    sites                    = "privatelink.azurewebsites.net",
    bot_framework_directline = "privatelink.directline.botframework.com",
    bot_framework_token      = "privatelink.token.botframework.com",
    open_ai                  = "privatelink.openai.azure.com",
    cognitive_account        = "privatelink.cognitiveservices.azure.com",
    cosmos_sql               = "privatelink.documents.azure.com",
    blob                     = "privatelink.blob.core.windows.net",
  }

  # Network variables
  virtual_network_address_space_mask_bits = tonumber(split("/", var.virtual_network_address_space)[1])
}

locals {
  tfvars = <<-EOT
# General variables
location        = "${var.location}"
location_openai = "${var.location_openai}"
environment     = "${var.environment}"
prefix          = "${var.prefix}"
tags            = {}

# Service variables
web_app_app_settings    = {}
web_app_code_path       = "../copilot"
bot_oauth_client_id     = "${local.application_client_id}"
bot_oauth_client_secret = "${local.application_password}"
bot_oauth_scopes = [
  "openid",
  "profile",
  "User.Read",
  "User.ReadBasic.All",
]

# Logging variables
log_analytics_workspace_id = "${module.log_analytics_workspace.log_analytics_workspace_id}"

# Network variables
vnet_id                       = "${azurerm_virtual_network.virtual_network.id}"
nsg_id                        = "${azurerm_network_security_group.network_security_group.id}"
route_table_id                = "${azurerm_route_table.route_table.id}"
subnet_cidr_web_app           = "${cidrsubnet(var.virtual_network_address_space, 28 - local.virtual_network_address_space_mask_bits, 0)}"
subnet_cidr_private_endpoints = "${cidrsubnet(var.virtual_network_address_space, 28 - local.virtual_network_address_space_mask_bits, 1)}"

# DNS variables
private_dns_zone_id_vault                    = "${azurerm_private_dns_zone.private_dns_zone["vault"].id}"
private_dns_zone_id_sites                    = "${azurerm_private_dns_zone.private_dns_zone["sites"].id}"
private_dns_zone_id_bot_framework_directline = "${azurerm_private_dns_zone.private_dns_zone["bot_framework_directline"].id}"
private_dns_zone_id_bot_framework_token      = "${azurerm_private_dns_zone.private_dns_zone["bot_framework_token"].id}"
private_dns_zone_id_open_ai                  = "${azurerm_private_dns_zone.private_dns_zone["open_ai"].id}"
private_dns_zone_id_cognitive_account        = "${azurerm_private_dns_zone.private_dns_zone["cognitive_account"].id}"
private_dns_zone_id_cosmos_sql               = "${azurerm_private_dns_zone.private_dns_zone["cosmos_sql"].id}"
private_dns_zone_id_blob                     = "${azurerm_private_dns_zone.private_dns_zone["blob"].id}"
  EOT
}
