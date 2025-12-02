module "cosmosdb_account" {
  source = "github.com/PerfectThymeTech/terraform-azurerm-modules//modules/cosmosdb?ref=main"
  providers = {
    azurerm = azurerm
    time    = time
  }

  location                                            = var.location
  resource_group_name                                 = azurerm_resource_group.resource_group_consumption.name
  tags                                                = var.tags
  cosmosdb_account_name                               = "${local.prefix}-cosmos001"
  cosmosdb_account_access_key_metadata_writes_enabled = true
  cosmosdb_account_analytical_storage_enabled         = false
  cosmosdb_account_automatic_failover_enabled         = false
  cosmosdb_account_backup = {
    type                = "Continuous"
    tier                = "Continuous7Days"
    storage_redundancy  = null
    retention_in_hours  = null
    interval_in_minutes = null
  }
  cosmosdb_account_capabilities = [
    # "EnableServerless" # TODO: Validate in a follow-up PR to save cost
  ]
  cosmosdb_account_capacity_total_throughput_limit = -1
  cosmosdb_account_consistency_policy = {
    consistency_level       = "Strong"
    max_interval_in_seconds = null
    max_staleness_prefix    = null
  }
  cosmosdb_account_cors_rules            = {}
  cosmosdb_account_default_identity_type = null
  cosmosdb_account_geo_location = [
    {
      location          = var.location
      failover_priority = 0
      zone_redundant    = false
    }
  ]
  cosmosdb_account_kind                          = "GlobalDocumentDB"
  cosmosdb_account_local_authentication_disabled = false
  cosmosdb_account_mongo_server_version          = null
  cosmosdb_account_partition_merge_enabled       = false
  diagnostics_configurations                     = []
  subnet_id                                      = azapi_resource.subnet_private_endpoints.id
  connectivity_delay_in_seconds                  = 0
  private_endpoint_subresource_names             = ["Sql"]
  private_dns_zone_id_cosmos_sql                 = var.private_dns_zone_id_cosmos_sql
  private_dns_zone_id_cosmos_mongodb             = ""
  private_dns_zone_id_cosmos_cassandra           = ""
  private_dns_zone_id_cosmos_gremlin             = ""
  private_dns_zone_id_cosmos_table               = ""
  private_dns_zone_id_cosmos_analytical          = ""
  private_dns_zone_id_cosmos_coordinator         = ""
  customer_managed_key                           = null
}

resource "azurerm_cosmosdb_sql_database" "cosmosdb_sql_database" {
  name                = "BotDb"
  account_name        = module.cosmosdb_account.cosmosdb_account_name
  resource_group_name = azurerm_resource_group.resource_group_consumption.name

  autoscale_settings {
    max_throughput = 1000
  }
}
