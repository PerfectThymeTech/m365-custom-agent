# Deployment of Reference Implementation for Microsoft 365 Custom Agent Reference Implementation

This document provides step-by-step instructions to deploy the Microsoft 365 Custom Agent Reference Implementation on top of the baseline infrastructure. It covers the deployment of application components, configuration settings, and verification steps to ensure the implementation is functioning correctly.

## Prerequisites

Before proceeding with the deployment, ensure that you have completed the steps outlined in the following documents:
- [Deployment Prerequisites](/docs/DeploymentPrerequisites.md)
- [Deployment of the Baseline infrastructure](/docs/DeploymentBaseline.md)

## Deployment Steps

1. **Navigate to the Reference Implementation Directory**: Change to the directory containing the Terraform configuration files for the reference implementation deployment.

    ```bash
    cd ./code/infra
    ```

2. **Update Terraform Variables**:

    1. If you have used the [Deployment of the Baseline infrastructure](/docs/DeploymentBaseline.md) to set up your environment, review and update the `vars.tf` file that has been automatically created in this directory. Ensure that the variables such as resource names, locations, and sizes align with your baseline deployment.

    2. If you are using your own resources, create a `vars.tfvars` file in this directory and define the necessary variables to customize the deployment parameters according to your requirements. Use the baseline provided below as a reference:

    ```hcl
    # General variables
    location        = "eastus2"
    location_openai = "eastus2"
    environment     = "dev"
    prefix          = "<your-prefix>"
    tags = {}

    # Service variables
    web_app_app_settings    = {}
    web_app_code_path       = "../copilot"
    bot_oauth_client_id     = ""
    bot_oauth_client_secret = ""
    bot_oauth_scopes = [
        "openid",
        "profile",
        "User.Read",
        "User.ReadBasic.All",
    ]

    # Logging variables
    log_analytics_workspace_id = "/subscriptions/<your-subscription-id>/resourceGroups/<your-resource-group>/providers/Microsoft.OperationalInsights/workspaces/<your-workspace>"

    # Network variables
    vnet_id                       = "/subscriptions/<your-subscription-id>/resourceGroups/<your-resource-group>/providers/Microsoft.Network/virtualNetworks/<your-vnet>"
    nsg_id                        = "/subscriptions/<your-subscription-id>/resourceGroups/<your-resource-group>/providers/Microsoft.Network/networkSecurityGroups/<your-nsg>"
    route_table_id                = "/subscriptions/<your-subscription-id>/resourceGroups/<your-resource-group>/providers/Microsoft.Network/routeTables/<your-route-table>"
    subnet_cidr_web_app           = "10.3.1.192/26"
    subnet_cidr_private_endpoints = "10.3.2.0/26"

    # DNS variables
    private_dns_zone_id_vault                    = "/subscriptions/<your-subscription-id>/resourceGroups/<your-resource-group>/providers/Microsoft.Network/privateDnsZones/privatelink.vaultcore.azure.net"
    private_dns_zone_id_sites                    = "/subscriptions/<your-subscription-id>/resourceGroups/<your-resource-group>/providers/Microsoft.Network/privateDnsZones/privatelink.azurewebsites.net"
    private_dns_zone_id_bot_framework_directline = "/subscriptions/<your-subscription-id>/resourceGroups/<your-resource-group>/providers/Microsoft.Network/privateDnsZones/privatelink.directline.botframework.com"
    private_dns_zone_id_bot_framework_token      = "/subscriptions/<your-subscription-id>/resourceGroups/<your-resource-group>/providers/Microsoft.Network/privateDnsZones/privatelink.token.botframework.com"
    private_dns_zone_id_open_ai                  = "/subscriptions/<your-subscription-id>/resourceGroups/<your-resource-group>/providers/Microsoft.Network/privateDnsZones/privatelink.openai.azure.com"
    private_dns_zone_id_cognitive_account        = "/subscriptions/<your-subscription-id>/resourceGroups/<your-resource-group>/providers/Microsoft.Network/privateDnsZones/privatelink.cognitiveservices.azure.com"
    private_dns_zone_id_cosmos_sql               = "/subscriptions/<your-subscription-id>/resourceGroups/<your-resource-group>/providers/Microsoft.Network/privateDnsZones/privatelink.documents.azure.com"
    private_dns_zone_id_blob                     = "/subscriptions/<your-subscription-id>/resourceGroups/<your-resource-group>/providers/Microsoft.Network/privateDnsZones/privatelink.blob.core.windows.net"
    ```

3. **Initialize Terraform**: Run the following command to initialize the Terraform configuration. This will download the necessary provider plugins.

    ```bash
    terraform init
    ```

4. **Login to Azure**: Log in to your Azure account using the Azure CLI. Open your terminal or command prompt and run the following command.

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

5. **Review the Deployment Plan**: Generate and review the deployment plan to understand the resources that will be created.

    ```bash
    terraform plan -var-file="vars.tfvars"
    ```

6. **Apply the Configuration**: Apply the configuration to deploy the reference implementation infrastructure.

    ```bash
    terraform apply -var-file="vars.tfvars"
    ```

    You will be prompted to confirm the action. Type `yes` to proceed.

7. **Verify the Deployment**: After the deployment is complete, verify that all resources have been created successfully by checking the Azure Portal or using the Azure CLI. Review the resource group named `<your-prefix>-bot-rg`, which should contain all the resources for the reference implementation.

8. **Agent Testing**: Navigate to the Azure Bot Service in the new resource group to test the deployed bot. Just click on "Test in Web Chat" to interact with the bot and ensure it is functioning as expected. Submit a few queries to validate its responses. Be aware that the web chat only supports file uploads up to 4MB in size.

## Next Steps

After successfully deploying the Microsoft 365 Custom Agent Reference Implementation, you can proceed with the following steps:
