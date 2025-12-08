resource "azurerm_linux_web_app" "linux_web_app" {
  name                = "${local.prefix}-app001"
  location            = var.location
  resource_group_name = azurerm_resource_group.resource_group_consumption.name
  tags                = merge(var.tags, { "hidden-link: /app-insights-resource-id" = module.application_insights.application_insights_id })
  identity {
    type = "UserAssigned"
    identity_ids = [
      module.user_assigned_identity.user_assigned_identity_id
    ]
  }

  app_settings                                   = local.web_app_app_settings
  client_affinity_enabled                        = false
  client_certificate_enabled                     = false
  client_certificate_exclusion_paths             = ""
  client_certificate_mode                        = "Required"
  enabled                                        = true
  ftp_publish_basic_authentication_enabled       = false
  https_only                                     = true
  key_vault_reference_identity_id                = module.user_assigned_identity.user_assigned_identity_id
  public_network_access_enabled                  = true
  service_plan_id                                = module.app_service_plan.service_plan_id
  virtual_network_subnet_id                      = azapi_resource.subnet_web_app.id
  webdeploy_publish_basic_authentication_enabled = false
  site_config {
    always_on             = true
    api_definition_url    = null
    api_management_api_id = null
    app_command_line      = "gunicorn --bind 0.0.0.0 --worker-class uvicorn.workers.UvicornWorker --timeout 600 app.main:app"
    application_stack {
      python_version = "3.13"
    }
    cors {
      allowed_origins = [
        "https://botservice.hosting.portal.azure.net",
        "https://hosting.onecloud.azure-test.net",
      ]
      support_credentials = true
    }
    container_registry_managed_identity_client_id = null
    container_registry_use_managed_identity       = null
    ftps_state                                    = "Disabled"
    http2_enabled                                 = true
    ip_restriction_default_action                 = "Allow" # "Deny"
    load_balancing_mode                           = "LeastRequests"
    local_mysql_enabled                           = false
    managed_pipeline_mode                         = "Integrated"
    minimum_tls_version                           = "1.2"
    remote_debugging_enabled                      = false
    remote_debugging_version                      = "VS2022"
    scm_ip_restriction_default_action             = "Allow" # "Deny"
    scm_use_main_ip_restriction                   = false
    scm_minimum_tls_version                       = "1.2"
    use_32_bit_worker                             = false
    vnet_route_all_enabled                        = true
    websockets_enabled                            = false
    worker_count                                  = 1
  }
}

data "azurerm_monitor_diagnostic_categories" "diagnostic_categories_linux_web_app" {
  resource_id = azurerm_linux_web_app.linux_web_app.id
}

resource "azurerm_monitor_diagnostic_setting" "diagnostic_setting_linux_web_app" {
  name                       = "logAnalytics"
  target_resource_id         = azurerm_linux_web_app.linux_web_app.id
  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.log_analytics_workspace.id

  dynamic "enabled_log" {
    iterator = entry
    for_each = data.azurerm_monitor_diagnostic_categories.diagnostic_categories_linux_web_app.log_category_groups
    content {
      category_group = entry.value
    }
  }

  dynamic "metric" {
    iterator = entry
    for_each = data.azurerm_monitor_diagnostic_categories.diagnostic_categories_linux_web_app.metrics
    content {
      category = entry.value
      enabled  = true
    }
  }
}

resource "azurerm_private_endpoint" "linux_web_app_private_endpoint" {
  name                = "${azurerm_linux_web_app.linux_web_app.name}-pe"
  location            = var.location
  resource_group_name = azurerm_resource_group.resource_group_consumption.name
  tags                = var.tags

  custom_network_interface_name = "${azurerm_linux_web_app.linux_web_app.name}-nic"
  private_service_connection {
    name                           = "${azurerm_linux_web_app.linux_web_app.name}-pe"
    is_manual_connection           = false
    private_connection_resource_id = azurerm_linux_web_app.linux_web_app.id
    subresource_names              = ["sites"]
  }
  subnet_id = azapi_resource.subnet_private_endpoints.id
  dynamic "private_dns_zone_group" {
    for_each = var.private_dns_zone_id_sites == "" ? [] : [1]
    content {
      name = "${azurerm_linux_web_app.linux_web_app.name}-arecord"
      private_dns_zone_ids = [
        var.private_dns_zone_id_sites
      ]
    }
  }

  lifecycle {
    ignore_changes = [
      private_dns_zone_group
    ]
  }
}
