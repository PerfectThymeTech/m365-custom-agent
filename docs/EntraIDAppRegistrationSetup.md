# Entra ID App Registration Setup for SSO

This document provides step-by-step instructions to set up an Entra ID App Registration to enable Single Sign-On (SSO) for your bot application. Follow these steps to create and configure the necessary App Registration in your Entra ID tenant.

## Prerequisites

- An Azure account with the necessary permissions to create App Registrations in Entra ID.
  - If you create the App Registration using a service principal, ensure it has either the `Application.ReadWrite.OwnedBy` or `Application.ReadWrite.All` permission.
  - If you create it using a user account, ensure you have either the `Application Administrator` or `Global Administrator` role.

## Steps to Set Up Entra ID App Registration

1. **Log in to the Azure Portal**:

    Navigate to the [Azure Portal](https://portal.azure.com/) and log in with your Azure account.

2. **Navigate to Entra ID**:

    In the Azure Portal, search for "Entra ID" in the search bar and select "Microsoft Entra ID" from the results.

3. **Create a New App Registration**:

   - In the Entra ID overview page, select "App registrations" from the left-hand menu.
   - Click on the "New registration" button at the top.
   - Provide a name for your application (e.g., "MyCopilotSSO").
   - Select the appropriate supported account types based on your requirements. We recommend selecting "Accounts in this organizational directory only (Single tenant)" to avoid external tenants from using your agent.
   - For the Redirect URI, select "Web" and enter the correct URL based on the selected data residency.
   - Click "Register" to create the App Registration.

   | Data Residency | Redirect URI |
   |----------------|-----|
   | `none`         | `https://token.botframework.com/.auth/web/redirect` |
   | `europe`       | `https://europe.token.botframework.com/.auth/web/redirect` |
   | `us`           | `https://unitedstates.token.botframework.com/.auth/web/redirect` |
   | `india`        | `https://india.token.botframework.com/.auth/web/redirect` |
   | `gov`          | `https://token.botframework.azure.us/.auth/web/redirect` |

4. **Follow the steps on Microsoft Learn**:

    Open the [Microsoft Learn Page which walks you through the configuration of the new app registration](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/authentication/bot-sso-register-aad?tabs=windows#enable-sso-in-microsoft-entra-id). Please consider the following notes:

    - When configuring the authorized client applications, make sure you at least add the app id for the Teams mobile and desktop application and the Teams web application.
    - You do **NOT** have to configure the redirect URL of your app again. You already completed this in step 3.
    - Do **NOT** configure the messaging endpoint for your bot resource as this will be take care of by the Terraform deployment.
    - Do **NOT** configure the OAuth connection for your bot resource in the Azure Portal. The Terraform deployment will take care of that.

5. **Configure API permissions**:

    - Open the API permissions panel of your App Registration.
    - Click on "Add a permission".
    - Select "Microsoft Graph".
    - Choose "Delegated permissions".
    - Add the following permissions:
      - `openid`
      - `profile`
      - `User.Read`
      - `User.ReadBasic.All`
    - Click "Add permissions" to save.
    - Finally, click on "Grant admin consent for <your-tenant>" to grant the permissions.

6. **Obtain Client ID and Client Secret**:

    - In the App Registration overview page, copy the "Application (client) ID". This will be used as the `bot_oauth_client_id`.
    - If you have already created a client secret during the Microsoft Learn steps, you can use that as a value for `bot_oauth_client_secret`. If you have taken note of it, skip to the next step. Otherwise, follow these steps to create a new client secret:
      - Navigate to "Certificates & secrets" in the left-hand menu.
      - Click on "New client secret", provide a description, and set an expiration period.
      - Click "Add" and copy the generated client secret value. This will be used as the `bot_oauth_client_secret`.

7. **Integrating Entra ID App Registration with Terraform Deployment**:

    To enable SSO for your bot application during the Terraform deployment of the reference implementation, you need to provide the `bot_oauth_client_id` and `bot_oauth_client_secret` values obtained from the App Registration setup. Update your `vars.tfvars` file in the [`/code/infra`](/code/infra/) directory with the values of your app registration.

## Next Steps

Proceed with the deployment of the reference implementation by following the steps outlined in the [Deployment of the Reference Implementation](/docs/DeploymentReferenceImplementation.md) document.
