module "ai_foundry" {
  source = "github.com/PerfectThymeTech/terraform-azurerm-modules//modules/aifoundrybasic?ref=main"
  providers = {
    azurerm = azurerm
    azapi   = azapi
    time    = time
  }

  location                                          = var.location_openai
  location_private_endpoint                         = var.location
  resource_group_name                               = azurerm_resource_group.resource_group_consumption.name
  tags                                              = var.tags
  ai_services_name                                  = "${local.prefix}-aif001"
  ai_services_sku                                   = "S0"
  ai_services_firewall_bypass_azure_services        = true
  ai_services_outbound_network_access_restricted    = true
  ai_services_outbound_network_access_allowed_fqdns = []
  ai_services_local_auth_enabled                    = false
  ai_services_projects = {
    project001 = {
      description  = "project001"
      display_name = "Project 001"
    }
  }
  ai_services_deployments               = {}
  diagnostics_configurations            = local.diagnostics_configurations
  subnet_id                             = azapi_resource.subnet_private_endpoints.id
  connectivity_delay_in_seconds         = var.connectivity_delay_in_seconds
  private_dns_zone_id_ai_services       = var.private_dns_zone_id_ai_services
  private_dns_zone_id_cognitive_account = var.private_dns_zone_id_cognitive_account
  private_dns_zone_id_open_ai           = var.private_dns_zone_id_open_ai
  customer_managed_key                  = null
}

resource "azurerm_cognitive_deployment" "cognitive_deployment_gpt_5_2" {
  name                 = "gpt-5.2"
  cognitive_account_id = module.ai_foundry.ai_services_id

  model {
    format  = "OpenAI"
    name    = "gpt-5.2"
    version = "2025-12-11"
  }
  sku {
    capacity = 250
    name     = "GlobalStandard"
  }
  version_upgrade_option = "OnceNewDefaultVersionAvailable"
}

resource "azurerm_cognitive_deployment" "cognitive_deployment_gpt_5_mini" {
  name                 = "gpt-5-mini"
  cognitive_account_id = module.ai_foundry.ai_services_id

  model {
    format  = "OpenAI"
    name    = "gpt-5-mini"
    version = "2025-08-07"
  }
  sku {
    capacity = 250
    name     = "GlobalStandard"
  }
  version_upgrade_option = "OnceNewDefaultVersionAvailable"
}
