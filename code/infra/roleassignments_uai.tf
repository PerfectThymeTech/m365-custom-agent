# Cognitive Service role assignments
resource "azurerm_role_assignment" "uai_role_assignment_open_ai_cognitive_services_openai_user" {
  description          = "Required for accessing azure open ai from the web app."
  scope                = module.azure_open_ai.cognitive_account_id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = module.user_assigned_identity.user_assigned_identity_principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "uai_role_assignment_document_intelligence_cognitive_services_user" {
  description          = "Required for accessing azure open ai from the web app."
  scope                = module.document_intelligence.cognitive_account_id
  role_definition_name = "Cognitive Services User"
  principal_id         = module.user_assigned_identity.user_assigned_identity_principal_id
  principal_type       = "ServicePrincipal"
}

# Key Vault role assignments
resource "azurerm_role_assignment" "uai_role_assignment_key_vault_secrets_user" {
  description          = "Required for accessing secrets in the key vault from the web app app settings."
  scope                = module.key_vault.key_vault_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = module.user_assigned_identity.user_assigned_identity_principal_id
  principal_type       = "ServicePrincipal"
}

# Application Insights role assignments
resource "azurerm_role_assignment" "uai_role_assignment_application_insights_monitoring_metrics_publisher" {
  description          = "Required for publishing logs in the application insights instance from the web app app settings."
  scope                = module.application_insights.application_insights_id
  role_definition_name = "Monitoring Metrics Publisher"
  principal_id         = module.user_assigned_identity.user_assigned_identity_principal_id
  principal_type       = "ServicePrincipal"
}

# Cosmos DB role assignments
resource "azurerm_cosmosdb_sql_role_assignment" "uai_cosmosdb_sql_role_assignment_database" {
  resource_group_name = azurerm_resource_group.resource_group_consumption.name
  account_name        = module.cosmosdb_account.cosmosdb_account_name
  role_definition_id  = data.azurerm_cosmosdb_sql_role_definition.cosmosdb_sql_role_definition.id
  principal_id        = module.user_assigned_identity.user_assigned_identity_principal_id
  scope               = "${module.cosmosdb_account.cosmosdb_account_id}/dbs/${azurerm_cosmosdb_sql_database.cosmosdb_sql_database.name}"
}
