# General variables
variable "location" {
  description = "Specifies the location for all Azure resources."
  type        = string
  sensitive   = false
}

variable "location_openai" {
  description = "Specifies the location for Azure Open AI."
  type        = string
  sensitive   = false
}

variable "environment" {
  description = "Specifies the environment of the deployment."
  type        = string
  sensitive   = false
  default     = "dev"
  validation {
    condition     = contains(["int", "dev", "tst", "qa", "uat", "prd"], var.environment)
    error_message = "Please use an allowed value: \"int\", \"dev\", \"tst\", \"qa\", \"uat\" or \"prd\"."
  }
}

variable "prefix" {
  description = "Specifies the prefix for all resources created in this deployment."
  type        = string
  sensitive   = false
  validation {
    condition     = length(var.prefix) >= 2 && length(var.prefix) <= 10
    error_message = "Please specify a prefix with more than two and less than 10 characters."
  }
}

variable "tags" {
  description = "Specifies the tags that you want to apply to all resources."
  type        = map(string)
  sensitive   = false
  default     = {}
}

# Service variables
variable "web_app_app_settings" {
  description = "Specifies the web app settings."
  type        = map(string)
  sensitive   = false
}

variable "web_app_code_path" {
  description = "Specifies the code location of the web app."
  type        = string
  sensitive   = false
  default     = ""
}

variable "bot_oauth_client_id" {
  description = "Specifies the client id of the Entra ID oauth app."
  type        = string
  sensitive   = true
  default     = ""
}

variable "bot_oauth_unique_identifier" {
  description = "Specifies the unique identifier of the Entra ID oauth app."
  type        = string
  sensitive   = false
  default     = ""
}

variable "bot_oauth_token_exchange_url" {
  description = "Specifies the token exchange url of the Entra ID oauth app."
  type        = string
  sensitive   = false
  default     = ""
}

variable "bot_oauth_federated_client_id" {
  description = "Specifies the federated client id of the Entra ID oauth app."
  type        = string
  sensitive   = false
  default     = ""
}

variable "bot_oauth_federated_credential_issuer" {
  description = "Specifies the federated credential issuer of the Entra ID oauth app."
  type        = string
  sensitive   = false
  default     = ""
}

variable "bot_oauth_federated_credential_value" {
  description = "Specifies the federated credential value of the Entra ID oauth app."
  type        = string
  sensitive   = false
  default     = ""
}

variable "bot_oauth_scopes" {
  description = "Specifies the scopes of the Entra ID oauth app."
  type        = list(string)
  sensitive   = false
  default     = []
}

variable "user_assigned_identity_id" {
  description = "Specifies the resource ID of the user assigned identity used for SSO with federated credentials."
  type        = string
  sensitive   = false
  validation {
    condition     = length(split("/", var.user_assigned_identity_id)) == 9
    error_message = "Please specify a valid resource ID."
  }
}

# Logging variables
variable "log_analytics_workspace_id" {
  description = "Specifies the resource ID of the log analytics workspace used for collecting logs."
  type        = string
  sensitive   = false
  validation {
    condition     = length(split("/", var.log_analytics_workspace_id)) == 9
    error_message = "Please specify a valid resource ID."
  }
}

# Network variables
variable "connectivity_delay_in_seconds" {
  description = "Specifies the delay in seconds after the private endpoint deployment (required for the DNS automation via Policies)."
  type        = number
  sensitive   = false
  nullable    = false
  default     = 120
  validation {
    condition     = var.connectivity_delay_in_seconds >= 0
    error_message = "Please specify a valid non-negative number."
  }
}

variable "vnet_id" {
  description = "Specifies the resource ID of the Vnet used for the Azure Function."
  type        = string
  sensitive   = false
  validation {
    condition     = length(split("/", var.vnet_id)) == 9
    error_message = "Please specify a valid resource ID."
  }
}

variable "nsg_id" {
  description = "Specifies the resource ID of the default network security group for the Azure Function."
  type        = string
  sensitive   = false
  validation {
    condition     = length(split("/", var.nsg_id)) == 9
    error_message = "Please specify a valid resource ID."
  }
}

variable "route_table_id" {
  description = "Specifies the resource ID of the default route table for the Azure Function."
  type        = string
  sensitive   = false
  validation {
    condition     = length(split("/", var.route_table_id)) == 9
    error_message = "Please specify a valid resource ID."
  }
}

variable "subnet_cidr_web_app" {
  description = "Specifies the subnet cidr range for the web app subnet."
  type        = string
  sensitive   = false
  validation {
    condition     = length(split("/", var.subnet_cidr_web_app)) == 2
    error_message = "Please specify a valid subnet cidr range."
  }
}

variable "subnet_cidr_private_endpoints" {
  description = "Specifies the subnet cidr range for private endpoints."
  type        = string
  sensitive   = false
  validation {
    condition     = length(split("/", var.subnet_cidr_private_endpoints)) == 2
    error_message = "Please specify a valid subnet cidr range."
  }
}

# DNS variables
variable "private_dns_zone_id_vault" {
  description = "Specifies the resource ID of the private DNS zone for Azure Key Vault. Not required if DNS A-records get created via Azure Policy."
  type        = string
  sensitive   = false
  default     = ""
  validation {
    condition     = var.private_dns_zone_id_vault == "" || (length(split("/", var.private_dns_zone_id_vault)) == 9 && endswith(var.private_dns_zone_id_vault, "privatelink.vaultcore.azure.net"))
    error_message = "Please specify a valid resource ID for the private DNS Zone."
  }
}

variable "private_dns_zone_id_sites" {
  description = "Specifies the resource ID of the private DNS zone for Azure Websites. Not required if DNS A-records get created via Azue Policy."
  type        = string
  sensitive   = false
  default     = ""
  validation {
    condition     = var.private_dns_zone_id_sites == "" || (length(split("/", var.private_dns_zone_id_sites)) == 9 && endswith(var.private_dns_zone_id_sites, "privatelink.azurewebsites.net"))
    error_message = "Please specify a valid resource ID for the private DNS Zone."
  }
}

variable "private_dns_zone_id_bot_framework_directline" {
  description = "Specifies the resource ID of the private DNS zone for the bot framework directline. Not required if DNS A-records get created via Azure Policy."
  type        = string
  sensitive   = false
  default     = ""
  validation {
    condition     = var.private_dns_zone_id_bot_framework_directline == "" || (length(split("/", var.private_dns_zone_id_bot_framework_directline)) == 9 && endswith(var.private_dns_zone_id_bot_framework_directline, "privatelink.directline.botframework.com"))
    error_message = "Please specify a valid resource ID for the private DNS Zone."
  }
}

variable "private_dns_zone_id_bot_framework_token" {
  description = "Specifies the resource ID of the private DNS zone for the bot framework token. Not required if DNS A-records get created via Azure Policy."
  type        = string
  sensitive   = false
  default     = ""
  validation {
    condition     = var.private_dns_zone_id_bot_framework_token == "" || (length(split("/", var.private_dns_zone_id_bot_framework_token)) == 9 && endswith(var.private_dns_zone_id_bot_framework_token, "privatelink.token.botframework.com"))
    error_message = "Please specify a valid resource ID for the private DNS Zone."
  }
}

variable "private_dns_zone_id_cognitive_account" {
  description = "Specifies the resource ID of the private DNS zone for Azure Cognitive Services. Not required if DNS A-records get created via Azure Policy."
  type        = string
  sensitive   = false
  default     = ""
  validation {
    condition     = var.private_dns_zone_id_cognitive_account == "" || (length(split("/", var.private_dns_zone_id_cognitive_account)) == 9 && (endswith(var.private_dns_zone_id_cognitive_account, "privatelink.cognitiveservices.azure.com")))
    error_message = "Please specify a valid resource ID for the private DNS Zone."
  }
}

variable "private_dns_zone_id_open_ai" {
  description = "Specifies the resource ID of the private DNS zone for Azure Open AI. Not required if DNS A-records get created via Azure Policy."
  type        = string
  sensitive   = false
  default     = ""
  validation {
    condition     = var.private_dns_zone_id_open_ai == "" || (length(split("/", var.private_dns_zone_id_open_ai)) == 9 && endswith(var.private_dns_zone_id_open_ai, "privatelink.openai.azure.com"))
    error_message = "Please specify a valid resource ID for the private DNS Zone."
  }
}

variable "private_dns_zone_id_cosmos_sql" {
  description = "Specifies the resource ID of the private DNS zone for cosmos db sql. Not required if DNS A-records get created via Azure Policy."
  type        = string
  sensitive   = false
  default     = ""
  validation {
    condition     = var.private_dns_zone_id_cosmos_sql == "" || (length(split("/", var.private_dns_zone_id_cosmos_sql)) == 9 && endswith(var.private_dns_zone_id_cosmos_sql, "privatelink.documents.azure.com"))
    error_message = "Please specify a valid resource ID for the private DNS Zone."
  }
}

variable "private_dns_zone_id_blob" {
  description = "Specifies the resource ID of the private DNS zone for blob storage. Not required if DNS A-records get created via Azure Policy."
  type        = string
  sensitive   = false
  default     = ""
  validation {
    condition     = var.private_dns_zone_id_blob == "" || (length(split("/", var.private_dns_zone_id_blob)) == 9 && endswith(var.private_dns_zone_id_blob, "privatelink.blob.core.windows.net"))
    error_message = "Please specify a valid resource ID for the private DNS Zone."
  }
}
