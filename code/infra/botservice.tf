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
    app_id        = module.user_assigned_identity.user_assigned_identity_client_id
    app_msi_id    = module.user_assigned_identity.user_assigned_identity_id
    app_tenant_id = module.user_assigned_identity.user_assigned_identity_tenant_id
    app_type      = "UserAssignedMSI"
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

resource "azurerm_bot_connection" "bot_connection_user_authorization_graph_oauth" {
  count = var.bot_oauth_client_id != "" && var.bot_oauth_client_secret != "" ? 1 : 0

  name                = local.bot_connection_user_authorization_graph_oauth_name
  bot_name            = module.bot_service.bot_service_name
  location            = "global"
  resource_group_name = azurerm_resource_group.resource_group_consumption.name

  client_id     = var.bot_oauth_client_id
  client_secret = var.bot_oauth_client_secret
  parameters = {
    "tenantId" = data.azurerm_client_config.current.tenant_id
  }
  service_provider_name = "Aadv2" # supported = wunderlist,google,pinterest,appFigures,facebook,SkypeForBusiness,outlook,SharePointOnline,Aadb2c,Aadv2,Aadv2WithCerts,FactSet,linkedin,trello,SharepointServer,oauth2,slack,zendesk,DynamicsCrmOnline,Aad,smartsheet,flickr,Office365,onedrive,basecamp,instagram,mailchimp,Office365User,echosign,live,oauth2generic,spotify,tumblr,AWeber,marketo,dropbox,box,yammer,intuit,uservoice,salesforce,todoist,github,docusign,stripe,bitly,lithium,sugarcrm
  scopes                = join(" ", var.bot_oauth_scopes)
}

resource "azurerm_bot_channel_ms_teams" "bot_channel_ms_teams" {
  bot_name            = module.bot_service.bot_service_name
  location            = "global"
  resource_group_name = azurerm_resource_group.resource_group_consumption.name

  calling_enabled        = false
  calling_web_hook       = null
  deployment_environment = "CommercialDeployment"
}
