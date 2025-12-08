# Deployment of Baseline for Microsoft 365 Custom Agent Reference Implementation

This document outlines the steps to deploy the baseline infrastructure and services required for the Microsoft 365 Custom Agent Reference Implementation using Terraform. The deployment includes setting up necessary Azure resources, configuring networking, and monitoring resources.

## Prerequisites

Before proceeding with the deployment, ensure that you have followed the steps in the [Deployment Prerequisites](/docs/DeploymentPrerequisites.md) document to set up your environment.

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

3. **Update Terraform Variables**: Review and update the `variables.tf` file to customize the deployment parameters such as the prefix, locations, and sizes according to your requirements.

4. **Initialize Terraform**: Run the following command to initialize the Terraform configuration. This will download the necessary provider plugins.

    ```bash
    terraform init
    ```

5. **Login to Azure**: Log in to your Azure account using the Azure CLI. Open your terminal or command prompt and run the following command.

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

6. **Review the Deployment Plan**: Generate and review the deployment plan to understand the resources that will be created.

    ```bash
    terraform plan -var-file="vars.tfvars"
    ```

7. **Apply the Configuration**: Apply the configuration to deploy the baseline infrastructure.

    ```bash
    terraform apply -var-file="vars.tfvars"
    ```
    You will be prompted to confirm the action. Type `yes` to proceed.

8. **Verify the Deployment**: After the apply command completes, verify that the resources have been created successfully in your Azure subscription by checking the Azure Portal. You should see a resource group with the name `<your-prefix>-prereqs-rg` which will contain all required resources for the main deployment.

9. **Verify Terraform Variables file**: The Terraform deployment automatically created a `vars.tfvars` file in [./code/infra](/code/infra/). Please review the file, which has all the required variables for the main deployment.

## Next Steps

With the baseline infrastructure deployed, you can now proceed to deploy the main components of the Microsoft 365 Custom Agent Reference Implementation. Follow the instructions in the [Deployment Reference Implementation Guide](/docs/DeploymentReferenceImplementation.md) to continue with the deployment process.
