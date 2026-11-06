resource "azurerm_private_dns_zone" "private_dns_zone" {
  for_each = local.private_dns_zone_names

  name                = each.value
  resource_group_name = azurerm_resource_group.resource_group.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "private_dns_zone_virtual_network_links" {
  for_each = local.private_dns_zone_names

  name = "${each.key}-${azurerm_virtual_network.virtual_network.name}"
  tags = var.tags

  private_dns_zone_id = azurerm_private_dns_zone.private_dns_zone[each.key].id
  virtual_network_id  = azurerm_virtual_network.virtual_network.id
}
