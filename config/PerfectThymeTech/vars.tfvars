# General variables
location        = "northeurope"
location_openai = "swedencentral"
environment     = "dev"
prefix          = "cop"
tags = {
  workload = "m365-copilot"
}

# Service variables
web_app_app_settings = {}
bot_oauth_scopes = [
  "openid",
  "profile",
  "User.Read",
  "User.ReadBasic.All",
]

# Logging variables
log_analytics_workspace_id = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-logging-rg/providers/Microsoft.OperationalInsights/workspaces/ptt-dev-log001"

# Network variables
vnet_id                       = "/subscriptions/1fdab118-1638-419a-8b12-06c9543714a0/resourceGroups/ptt-dev-networking-rg/providers/Microsoft.Network/virtualNetworks/spoke-ptt-dev-vnet001"
nsg_id                        = "/subscriptions/1fdab118-1638-419a-8b12-06c9543714a0/resourceGroups/ptt-dev-networking-rg/providers/Microsoft.Network/networkSecurityGroups/ptt-dev-default-nsg001"
route_table_id                = "/subscriptions/1fdab118-1638-419a-8b12-06c9543714a0/resourceGroups/ptt-dev-networking-rg/providers/Microsoft.Network/routeTables/ptt-dev-default-rt001"
subnet_cidr_web_app           = "10.3.1.192/26"
subnet_cidr_private_endpoints = "10.3.2.0/26"

# DNS variables
private_dns_zone_id_vault                    = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-privatedns-rg/providers/Microsoft.Network/privateDnsZones/privatelink.vaultcore.azure.net"
private_dns_zone_id_sites                    = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-privatedns-rg/providers/Microsoft.Network/privateDnsZones/privatelink.azurewebsites.net"
private_dns_zone_id_bot_framework_directline = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-privatedns-rg/providers/Microsoft.Network/privateDnsZones/privatelink.directline.botframework.com"
private_dns_zone_id_bot_framework_token      = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-privatedns-rg/providers/Microsoft.Network/privateDnsZones/privatelink.token.botframework.com"
private_dns_zone_id_open_ai                  = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-privatedns-rg/providers/Microsoft.Network/privateDnsZones/privatelink.openai.azure.com"
private_dns_zone_id_cosmos_sql               = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-privatedns-rg/providers/Microsoft.Network/privateDnsZones/privatelink.documents.azure.com"
private_dns_zone_id_blob                     = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-privatedns-rg/providers/Microsoft.Network/privateDnsZones/privatelink.blob.core.windows.net"
private_dns_zone_id_data_factory             = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-privatedns-rg/providers/Microsoft.Network/privateDnsZones/privatelink.datafactory.azure.net"
