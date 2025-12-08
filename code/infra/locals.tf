locals {
  # Naming locals
  prefix = "${lower(var.prefix)}-${var.environment}"
  resource_providers_to_register = [
    "Microsoft.Authorization",
    "Microsoft.BotService",
    "Microsoft.CognitiveServices",
    "microsoft.insights",
    "Microsoft.KeyVault",
    "Microsoft.ManagedIdentity",
    "Microsoft.Network",
    "Microsoft.Resources",
    "Microsoft.Web",
  ]

  # Web app locals
  app_settings_default = {
    # Configuration app settings
    APPLICATIONINSIGHTS_CONNECTION_STRING      = module.application_insights.application_insights_connection_string
    ApplicationInsightsAgent_EXTENSION_VERSION = "~3"
    SCM_DO_BUILD_DURING_DEPLOYMENT             = "1"
    WEBSITE_CONTENTOVERVNET                    = "1"

    # Auth app settings
    AUTH_TYPE                 = "UserManagedIdentity"
    TENANT_ID                 = data.azurerm_client_config.current.tenant_id
    CLIENT_ID                 = module.user_assigned_identity.user_assigned_identity_client_id
    AAD_OAUTH_CONNECTION_NAME = local.bot_connection_aadv2_oauth_name

    # Azure Document Intelligence settings
    AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = module.document_intelligence.cognitive_account_endpoint
    AZURE_DOCUMENT_INTELLIGENCE_API_KEY  = module.document_intelligence.cognitive_account_primary_access_key

    # Cosmos DB settings
    AZURE_COSMOS_ENDPOINT     = module.cosmosdb_account.cosmosdb_account_endpoint
    AZURE_COSMOS_KEY          = module.cosmosdb_account.cosmosdb_account_primary_key
    AZURE_COSMOS_DATABASE_ID  = azurerm_cosmosdb_sql_database.cosmosdb_sql_database.name
    AZURE_COSMOS_CONTAINER_ID = local.cosmosdb_sql_container_name

    # Azure Open AI app settings
    AZURE_OPENAI_ENDPOINT       = module.azure_open_ai.cognitive_account_endpoint
    AZURE_OPENAI_API_KEY        = module.azure_open_ai.cognitive_account_primary_access_key
    AZURE_OPENAI_MODEL_NAME     = azurerm_cognitive_deployment.cognitive_deployment_gpt_5_1.name
    AZURE_OPENAI_MODEL_SLM_NAME = azurerm_cognitive_deployment.cognitive_deployment_gpt_5_mini.name

    # Prompt settings
    INSTRUCTIONS_DOCUMENT_AGENT          = data.local_file.file_instructions_document_agent.content
    INSTRUCTIONS_SUGGESTED_ACTIONS_AGENT = data.local_file.file_instructions_suggested_actions_agent.content
  }
  web_app_app_settings = merge(local.app_settings_default, var.web_app_app_settings)

  # Resource locals
  virtual_network = {
    resource_group_name = split("/", var.vnet_id)[4]
    name                = split("/", var.vnet_id)[8]
  }
  network_security_group = {
    resource_group_name = split("/", var.nsg_id)[4]
    name                = split("/", var.nsg_id)[8]
  }
  route_table = {
    resource_group_name = split("/", var.route_table_id)[4]
    name                = split("/", var.route_table_id)[8]
  }
  log_analytics_workspace = {
    subscription_id     = split("/", var.log_analytics_workspace_id)[2]
    resource_group_name = split("/", var.log_analytics_workspace_id)[4]
    name                = split("/", var.log_analytics_workspace_id)[8]
  }

  # Storage locals
  storage_account_container_raw_name     = "raw"
  storage_account_container_curated_name = "curated"

  # Logging locals
  diagnostics_configurations = [
    {
      log_analytics_workspace_id = var.log_analytics_workspace_id
      storage_account_id         = ""
    }
  ]

  # CMK locals
  customer_managed_key = null

  # Other locals
  instructions_document_agent_path          = "${path.module}/../../docs/INSTRUCTIONS_DOCUMENT_AGENT.txt"
  instructions_suggested_actions_agent_path = "${path.module}/../../docs/INSTRUCTIONS_SUGGESTED_ACTIONS_AGENT.txt"
  cosmosdb_sql_container_name               = "bot-data"
  bot_connection_aadv2_oauth_name           = "aadv2-oauth"
}
