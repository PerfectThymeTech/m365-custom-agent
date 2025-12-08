data "azurerm_client_config" "current" {}

data "azurerm_virtual_network" "virtual_network" {
  name                = local.virtual_network.name
  resource_group_name = local.virtual_network.resource_group_name
}

data "azurerm_network_security_group" "network_security_group" {
  name                = local.network_security_group.name
  resource_group_name = local.network_security_group.resource_group_name
}

data "azurerm_route_table" "route_table" {
  name                = local.route_table.name
  resource_group_name = local.route_table.resource_group_name
}

data "azurerm_log_analytics_workspace" "log_analytics_workspace" {
  provider = azurerm.management

  name                = local.log_analytics_workspace.name
  resource_group_name = local.log_analytics_workspace.resource_group_name
}

data "local_file" "file_instructions_document_agent" {
  filename = local.instructions_document_agent_path
}

data "local_file" "file_instructions_suggested_actions_agent" {
  filename = local.instructions_suggested_actions_agent_path
}

data "archive_file" "file_web_app" {
  count = var.web_app_code_path != "" ? 1 : 0

  excludes    = ["${path.module}/${var.web_app_code_path}/.venv/**"]
  type        = "zip"
  source_dir  = "${path.module}/${var.web_app_code_path}"
  output_path = "${path.module}/${format("webapp-${azurerm_linux_web_app.linux_web_app.name}-%s.zip", formatdate("YYYY-MM-DD'-'hh_mm_ss", timestamp()))}"
}
