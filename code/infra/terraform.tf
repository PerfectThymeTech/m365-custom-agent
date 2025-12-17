terraform {
  required_version = ">=0.12"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "4.56.0"
    }
    azapi = {
      source  = "azure/azapi"
      version = "2.8.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "0.13.1"
    }
    local = {
      source  = "hashicorp/local"
      version = "2.6.1"
    }
    null = {
      source  = "hashicorp/null"
      version = "3.2.4"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "2.7.1"
    }
  }

  backend "azurerm" {
    environment          = "public"
    resource_group_name  = "<provided-via-config>"
    storage_account_name = "<provided-via-config>"
    container_name       = "<provided-via-config>"
    key                  = "<provided-via-config>"
    use_azuread_auth     = true
  }
}
