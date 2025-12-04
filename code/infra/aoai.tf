module "azure_open_ai" {
  source = "github.com/PerfectThymeTech/terraform-azurerm-modules//modules/aiservice?ref=main"
  providers = {
    azurerm = azurerm
    time    = time
  }

  location                                                = var.location_openai
  location_private_endpoint                               = var.location
  resource_group_name                                     = azurerm_resource_group.resource_group_consumption.name
  tags                                                    = var.tags
  cognitive_account_name                                  = "${local.prefix}-aoai001"
  cognitive_account_kind                                  = "OpenAI"
  cognitive_account_sku                                   = "S0"
  cognitive_account_firewall_bypass_azure_services        = false
  cognitive_account_outbound_network_access_restricted    = true
  cognitive_account_outbound_network_access_allowed_fqdns = []
  cognitive_account_local_auth_enabled                    = true # TODO: Change to false in a follow-up PR after updating code to use Managed Identity
  cognitive_account_deployments                           = {}
  diagnostics_configurations                              = local.diagnostics_configurations
  subnet_id                                               = azapi_resource.subnet_private_endpoints.id
  connectivity_delay_in_seconds                           = var.connectivity_delay_in_seconds
  private_dns_zone_id_cognitive_account                   = var.private_dns_zone_id_open_ai
  customer_managed_key                                    = local.customer_managed_key
}

resource "azurerm_cognitive_deployment" "cognitive_deployment_gpt_5_1" {
  name                 = "gpt-5.1"
  cognitive_account_id = module.azure_open_ai.cognitive_account_id

  model {
    format  = "OpenAI"
    name    = "gpt-5.1"
    version = "2025-11-13"
  }
  sku {
    capacity = 250
    name     = "GlobalStandard"
  }
  version_upgrade_option = "OnceNewDefaultVersionAvailable"
}

resource "azurerm_cognitive_deployment" "cognitive_deployment_gpt_5_mini" {
  name                 = "gpt-5-mini"
  cognitive_account_id = module.azure_open_ai.cognitive_account_id

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
