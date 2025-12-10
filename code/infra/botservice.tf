module "bot_service" {
  source = "github.com/PerfectThymeTech/terraform-azurerm-modules//modules/botservice?ref=main"
  providers = {
    azurerm = azurerm
    time    = time
  }

  location             = var.location
  resource_group_name  = azurerm_resource_group.resource_group_consumption.name
  tags                 = var.tags
  bot_service_name     = "${local.prefix}-bot001"
  bot_service_location = "global"
  bot_service_endpoint = "https://${azurerm_linux_web_app.linux_web_app.default_hostname}/api/v1/messages/message"
  bot_service_luis = {
    app_ids = []
    key     = null
  }
  bot_service_microsoft_app = {
    app_id        = var.bot_oauth_client_id
    app_msi_id    = null
    app_tenant_id = data.azurerm_client_config.current.tenant_id
    app_type      = "SingleTenant"
  }
  bot_service_sku                              = "S1"
  bot_service_icon_url                         = "https://docs.botframework.com/static/devportal/client/images/bot-framework-default.png"
  bot_service_streaming_endpoint_enabled       = true
  bot_service_public_network_access_enabled    = true
  bot_service_application_insights_id          = module.application_insights.application_insights_id
  bot_service_application_insights_key_enabled = false
  diagnostics_configurations                   = local.diagnostics_configurations
  subnet_id                                    = azapi_resource.subnet_private_endpoints.id
  connectivity_delay_in_seconds                = var.connectivity_delay_in_seconds
  private_dns_zone_id_bot_framework_directline = var.private_dns_zone_id_bot_framework_directline
  private_dns_zone_id_bot_framework_token      = var.private_dns_zone_id_bot_framework_token
  customer_managed_key                         = local.customer_managed_key
}

resource "azapi_resource" "bot_connection_aadv2_federated_credentials" {
  count = var.bot_oauth_client_id != "" && var.bot_oauth_unique_identifier != "" && var.bot_oauth_token_exchange_url != "" ? 1 : 0

  type      = "Microsoft.BotService/botServices/connections@2023-09-15-preview"
  parent_id = module.bot_service.bot_service_id
  name      = local.bot_connection_aadv2_federated_credentials_name
  location  = "global"

  body = {
    kind = "azurebot"
    properties = {
      clientId     = var.bot_oauth_client_id
      clientSecret = null
      parameters = [
        {
          key = "ClientId"
          value = var.bot_oauth_client_id
        },
        {
          key = "UniqueIdentifier"
          value = var.bot_oauth_unique_identifier
        },
        {
          key = "TokenExchangeUrl"
          value = var.bot_oauth_token_exchange_url
        },
        {
          key = "TenantId"
          value = data.azurerm_client_config.current.tenant_id
        },
      ]
      serviceProviderId = "c00b44ab-5e16-c44c-af26-2fd5bc55eb18" # Aadv2WithFic
      scopes            = join(" ", var.bot_oauth_scopes)
    }
  }
}

resource "azurerm_bot_channel_ms_teams" "bot_channel_ms_teams" {
  bot_name            = module.bot_service.bot_service_name
  location            = "global"
  resource_group_name = azurerm_resource_group.resource_group_consumption.name

  calling_enabled        = false
  calling_web_hook       = null
  deployment_environment = "CommercialDeployment"
}
