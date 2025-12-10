# General variables
variable "location" {
  description = "Specifies the location for all Azure resources."
  type        = string
  sensitive   = false
  default     = "eastus2"
}

variable "location_openai" {
  description = "Specifies the location for Azure Open AI."
  type        = string
  sensitive   = false
  default     = "eastus2"
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
variable "data_residency" {
  description = "Specifies the data residency requirements of the bot framework."
  type        = string
  sensitive   = false
  nullable    = false
  default     = "none"
  validation {
    condition     = contains(["none", "europe", "us", "india", "gov"], var.data_residency)
    error_message = "Please specify a valid data residency. Must be one of 'none', 'europe', 'us', 'india', or 'gov'."
  }
}

variable "entra_application_enabled" {
  description = "Specifies whether the Entra ID application should be created."
  type        = bool
  sensitive   = false
  nullable    = false
  default     = false
}

variable "encoded_tenant_id" {
  description = "Specifies the encoded tenant ID."
  type        = string
  sensitive   = false
  nullable    = false
}

variable "virtual_network_address_space" {
  description = "Specifies the virtual network address space."
  type        = string
  sensitive   = false
  nullable    = false
  default     = "10.0.0.0/20"
  validation {
    condition     = length(split("/", var.virtual_network_address_space)) == 2
    error_message = "Please specify a valid vnet cidr range."
  }
  validation {
    condition     = tonumber(split("/", var.virtual_network_address_space)[1]) <= 27
    error_message = "Please specify a valid vnet cidr range larger than 25."
  }
}
