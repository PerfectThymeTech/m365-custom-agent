module "storage_account" {
  source = "github.com/PerfectThymeTech/terraform-azurerm-modules//modules/storage?ref=main"
  providers = {
    azurerm = azurerm
    time    = time
  }

  location            = var.location
  resource_group_name = azurerm_resource_group.resource_group_consumption.name
  tags                = var.tags

  storage_account_name                            = replace("${local.prefix}-stg001", "-", "")
  storage_access_tier                             = "Hot"
  storage_account_type                            = "StorageV2"
  storage_account_tier                            = "Standard"
  storage_account_replication_type                = "ZRS"
  storage_account_allowed_copy_scope              = "AAD"
  storage_blob_change_feed_enabled                = false
  storage_blob_container_delete_retention_in_days = 7
  storage_blob_delete_retention_in_days           = 7
  storage_blob_cors_rules                         = {}
  storage_blob_last_access_time_enabled           = false
  storage_blob_versioning_enabled                 = false
  storage_is_hns_enabled                          = false
  storage_network_bypass                          = ["None"]
  storage_network_private_link_access = [
    "/subscriptions/${data.azurerm_client_config.current.subscription_id}/providers/Microsoft.Security/datascanners/storageDataScanner",
    "/subscriptions/${data.azurerm_client_config.current.subscription_id}/resourceGroups/*/providers/Microsoft.CognitiveServices/accounts/*",
  ]
  storage_public_network_access_enabled = true
  storage_nfsv3_enabled                 = false
  storage_sftp_enabled                  = false
  storage_shared_access_key_enabled     = false
  storage_container_names               = [local.storage_account_container_raw_name, local.storage_account_container_curated_name, ]
  storage_static_website                = []
  diagnostics_configurations            = local.diagnostics_configurations
  subnet_id                             = azapi_resource.subnet_private_endpoints.id
  connectivity_delay_in_seconds         = var.connectivity_delay_in_seconds
  private_endpoint_subresource_names    = ["blob"]
  private_dns_zone_id_blob              = var.private_dns_zone_id_blob
  private_dns_zone_id_file              = ""
  private_dns_zone_id_table             = ""
  private_dns_zone_id_queue             = ""
  private_dns_zone_id_web               = ""
  private_dns_zone_id_dfs               = ""
  customer_managed_key                  = local.customer_managed_key
}
