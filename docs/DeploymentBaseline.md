# Deployment of Baseline for Microsoft 365 Custom Agent Reference Implementation

This document outlines the steps to deploy the baseline infrastructure and services required for the Microsoft 365 Custom Agent Reference Implementation using Terraform. The deployment includes setting up necessary Azure resources, configuring networking, and monitoring resources.

## Prerequisites

Before proceeding with the deployment, ensure that you have followed the steps in the [Deployment Prerequisites](/docs/DeploymentPrerequisites.md) document to set up your environment.

## Notes

- This is an opttional deployment step. The baseline infrastructure is only required if you do not already have the necessary resources and configurations in place.
- The baseline deployment provisions foundational resources that the main implementation will build upon. This includes:
    - Virtual Networks
    - Network Security Groups
    - Route Tables
    - Private DNS Zones
    - Log Analytics Workspace
    - (optional) Entra ID App Registrations
- If you already have these resources configured in your Azure environment, you may choose to skip this step and proceed directly to the [Deployment of Reference Implementation](/docs/DeploymentReferenceImplementation.md).

## Deployment Steps

1. **Clone the Repository**: If you haven't already, clone the Microsoft 365 Custom Agent repository to your local machine.

    ```bash
    git clone https://github.com/PerfectThymeTech/m365-custom-agent.git
    cd m365-custom-agent
    ```

2. **Navigate to the Terraform Directory**: Change to the directory containing the Terraform configuration files for the baseline deployment.

    ```bash
    cd ./docs/prereqs
    ```

3. **Update Terraform Variable File**: Review and update the `vars.tf` file that has been created for you in the `./docs/prereqs` directory. Ensure that the variables such as the `prefix`, locations, and sizes align with your requirements.

    | Variable Name               | Description |
    |-----------------------------|-------------|
    | `location`                  | Azure region for resource deployment. |
    | `location_openai`           | Azure region for OpenAI resource. Please ensure you select a [region that supports GPT-5.1](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-models/concepts/models-sold-directly-by-azure?view=foundry-classic&tabs=global-standard-aoai%2Cstandard-chat-completions%2Cglobal-standard&pivots=azure-openai#gpt-51). |
    | `environment`               | Deployment environment (e.g., dev, tst, prd). |
    | `prefix`                    | A unique prefix for naming resources. |
    | `tags`                      | Tags to apply to all taggable resources. |
    | `data_residency`            | Data residency requirement (e.g., `none`, `europe`, `us`, `india`, `gov`). |
    | `entra_application_enabled` | Set to `true` to create Entra ID App Registrations for SSO, or `false` to skip. Only set this to `true` if you have the following Entra ID permissions: `Application Administrator` or `Global Administrator`. If you deploy with a service principal, you need one of the following permissions: `Application.ReadWrite.OwnedBy` or `Application.ReadWrite.All`. If you don't create the Entra ID App Registrations, you must provide your own client ID and client secret in the `vars.tfvars` file in the next deployment step. Ensure you follow the documentation for creating these credentials manually which you can find in the [Entra ID App Registration](./EntraIDAppRegistrationSetup.md) setup guide. |
    | `virtual_network_address_space` | Address space for the virtual network. |

4. **Set Environment Variables**: Set the necessary environment variables for Terraform. This includes specifying the Azure subscription ID.

    For Windows:
    ```pwsh
    $env:ARM_SUBSCRIPTION_ID = "<your-subscription-id>"
    ```

    For Linux/MacOS:
    ```bash
    export ARM_SUBSCRIPTION_ID="<your-subscription-id>"
    ```

5. **Initialize Terraform**: Run the following command to initialize the Terraform configuration. This will download the necessary provider plugins.

    ```bash
    terraform init
    ```

6. **Login to Azure**: Log in to your Azure account using the Azure CLI. Open your terminal or command prompt and run the following command.

    ```bash
    az login
    ```

    If you have access to multiple Entra ID Tenants, specify the desired tenant using the `--tenant` parameter:

    ```bash
    az login --tenant <tenant-id-or-name>
    ```

    Set the desired subscription context using the following command:

    ```bash
    az account set --subscription <subscription-id-or-name>
    ```

    You can verify the current subscription context by running:

    ```bash
    az account show
    ```

7. **Review the Deployment Plan**: Generate and review the deployment plan to understand the resources that will be created.

    ```bash
    terraform plan -var-file="vars.tfvars"
    ```

8. **Apply the Configuration**: Apply the configuration to deploy the baseline infrastructure.

    ```bash
    terraform apply -var-file="vars.tfvars"
    ```
    You will be prompted to confirm the action. Type `yes` to proceed.

9. **Verify the Deployment**: After the apply command completes, verify that the resources have been created successfully in your Azure subscription by checking the Azure Portal. You should see a resource group with the name `<your-prefix>-prereqs-rg` which will contain all required resources for the main deployment.

10. **Verify Terraform Variable File**: The Terraform deployment automatically created a `vars.tfvars` file in [./code/infra](/code/infra/). Please review the file, which has all the required variables for the main deployment.

## Next Steps

With the baseline infrastructure deployed, you can now proceed to deploy the main components of the Microsoft 365 Custom Agent Reference Implementation. Follow the instructions in the [Deployment Reference Implementation Guide](/docs/DeploymentReferenceImplementation.md) to continue with the deployment process.
