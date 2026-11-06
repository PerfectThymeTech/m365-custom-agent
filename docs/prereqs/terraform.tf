terraform {
  required_version = ">=0.12"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "5.12.0"
    }
    azapi = {
      source  = "azure/azapi"
      version = "2.13.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "3.8.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "0.14.2"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.9.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "2.9.0"
    }
  }
}
