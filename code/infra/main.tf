resource "azurerm_resource_group" "resource_group_consumption" {
  name     = "${local.prefix}-bot-rg"
  location = var.location
  tags     = var.tags
}
