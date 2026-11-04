# Deployment Prerequisites


## Software requirements

Before deploying the Microsoft 365 Custom Agent Reference Implementation, ensure you have the following software installed on your device:

1. **Azure CLI**: Install the Azure Command-Line Interface (CLI) to manage Azure resources from your local machine. Follow the installation guide at [Install Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli).
2. **Terraform**: Install Terraform to use Infrastructure as Code (IaC) if you plan on contributing to the Terraform project or deploying the project to your environment. Follow the guide at [Install Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli) to install the Terraform CLI.
3. **Visual Studio Code**: It is recommended to use Visual Studio Code as your code editor. Download it from [VS Code Downloads](https://code.visualstudio.com/download) and install the necessary extensions for Python and Azure development.
4. **Python 3.8+**: Ensure you have Python version 3.8 or higher installed on your machine if you plan in contributing to the Python project. You can download it from [Python Downloads](https://www.python.org/downloads/).
5. **uv Package Manager (Optional)**: The project uses the uv package manager for dependency management. If you plan in contributing to the Python project then install uv by following the instructions at [uv Documentation](https://docs.astral.sh/uv/#installation).
6. **Git**: Install Git to clone the repository and manage version control. You can download it from [Git Downloads](https://git-scm.com/downloads).

Once you have met all the prerequisites, you can proceed with the next section.

## Other Prerequisites

1. **Azure Subscription**: An active Azure subscription is required to deploy and manage resources. If you don't have one, you can create a free account at [Azure Free Account](https://azure.microsoft.com/free/).
2. **Permission to Create Resources**: Ensure that your Azure account has sufficient permissions at the subscription level to create and manage resources such as App Services, Azure Functions, and other related services. The following combination of roles is recommended:
   - Owner or
   - Contributor and User Access Administrator

## Verify Installation

After installing the required software, verify the installations by running the following commands in your terminal or command prompt:

```bash
az --version
terraform --version
python --version
uv --version
git --version
```

Each command should return the installed version of the respective software, confirming that the installation was successful.

## Set Azure Context

### Login to Azure

Before deploying the application, log in to your Azure account using the Azure CLI. Open your terminal or command prompt and run the following command:

```bash
az login
```

If you have access to multiple Entra ID Tenants, specify the desired tenant using the `--tenant` parameter:

```bash
az login --tenant <tenant-id-or-name>
```

### Set the Subscription context

Set the desired subscription context using the following command:

```bash
az account set --subscription <subscription-id-or-name>
```

You can verify the current subscription context by running:

```bash
az account show
```

This will display the details of the currently active subscription, ensuring that you are working within the correct context for your deployment.

## Test Terraform deployment

To verify that your environment is correctly set up for deployments with Terraform, you can perform a simple test by initializing a new Terraform configuration and applying it to create a basic resource in Azure. Follow these steps:

1. **Create a Test Directory**: Create a new directory for your test Terraform configuration.

    ```bash
    mkdir terraform-test
    cd terraform-test
    ```

2. **Create a Terraform Configuration File**: Create a file named `main.tf` and add the following content to define a simple Azure Resource Group.

    ```hcl
    terraform {
      required_providers {
        azurerm = {
          source  = "hashicorp/azurerm"
          version = "~> 5.0"
        }
      }
    }

    provider "azurerm" {
      resource_provider_registrations = "none"
      features {}
    }

    resource "azurerm_resource_group" "test" {
      name     = "terraform-test-rg"
      location = "East US"
    }
    ```

3. **Set Environment Variables**: Set the necessary environment variables for Terraform. This includes specifying the Azure subscription ID.

    For Windows:
    ```pwsh
    $env:ARM_SUBSCRIPTION_ID = "<your-subscription-id>"
    ```

    For Linux/MacOS:
    ```bash
    export ARM_SUBSCRIPTION_ID="<your-subscription-id>"
    ```

4. **Initialize Terraform**: Run the following command to initialize the Terraform configuration. This will download the necessary provider plugins.

    ```bash
    terraform init
    ```

5. **Apply the Configuration**: Apply the configuration to create the resource group in Azure.

    ```bash
    terraform apply
    ```
    You will be prompted to confirm the action. Type `yes` to proceed.

6. **Verify the Resource Creation**: After the apply command completes, verify that the resource group has been created in your Azure subscription by checking the Azure Portal or using the Azure CLI:

    ```bash
    az group show --name terraform-test-rg
    ```

7. **Clean Up**: Once you have verified that the resource group was created successfully, you can clean up by destroying the resources created during the test.

    ```bash
    terraform destroy
    ```
    You will be prompted to confirm the action. Type `yes` to proceed.

By following these steps, you can confirm that your environment is properly configured for deploying resources using Terraform in Azure. If you encounter any issues during this process, review the error messages for guidance on resolving them before proceeding with more complex deployments.

## Upgrading Existing Terraform Deployments

The baseline and application configurations use AzureRM `5.12.0`, AzAPI `2.13.0`, and time `0.14.2`, matching the versions tested in [terraform-azurerm-modules PR #177](https://github.com/PerfectThymeTech/terraform-azurerm-modules/pull/177). Module sources continue to track `main`, so PR #177 must be merged before initializing these configurations.

For an existing deployment, back up the Terraform state and run `terraform init -upgrade` in both [docs/prereqs](/docs/prereqs/) and [code/infra](/code/infra/), retaining the application's existing `-backend-config` argument. Then run `terraform validate` and review `terraform plan` with your usual variable file before applying either deployment.

AzureRM v5 does not register resource providers by default. Both configurations explicitly register the providers listed in their `locals.tf` files; the application list includes `Microsoft.DocumentDB` for Cosmos DB and `Microsoft.Storage` for storage accounts. The deployment identity needs permission to register these providers. The management provider keeps registration disabled, so the subscription hosting an existing Log Analytics workspace must already have its required providers registered.

No static-website import is needed for the supplied configuration because `storage_static_website` is empty. If you previously enabled a static website, follow PR #177's one-time import guidance for `azurerm_storage_account_static_website` before applying. The Application Insights and Cosmos DB module inputs ending in `local_authentication_disabled` remain supported and should not be inverted by callers.

## Next Steps

With the deployment prerequisites met and your environment verified, you are now ready to proceed with deploying the Microsoft 365 Custom Agent Reference Implementation. Follow the deployment instructions in the subsequent sections of the documentation which covers the [Deployment of the Baseline infrastructure](/docs/DeploymentBaseline.md).
