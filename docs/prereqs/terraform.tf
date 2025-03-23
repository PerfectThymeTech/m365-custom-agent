terraform {
  required_version = ">=0.12"

  required_providers {
    azuread = {
      source  = "hashicorp/azuread"
      version = "3.2.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "0.12.1"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.6.3"
    }
  }
}
