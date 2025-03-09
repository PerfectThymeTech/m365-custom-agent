terraform {
  required_version = ">=0.12"

  required_providers {
    azuread = {
      source  = "hashicorp/azuread"
      version = "3.0.2"
    }
    time = {
      source  = "hashicorp/time"
      version = "0.13.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.6.3"
    }
  }
}
