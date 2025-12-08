# Deployment of Teams App

This document outlines how to use the Agent through the Microsoft Teams channel.

## Prerequisites

Before proceeding with the deployment, ensure that you have completed the steps outlined in the following documents:
- [Deployment Prerequisites](/docs/DeploymentPrerequisites.md)
- [Deployment of the Baseline infrastructure](/docs/DeploymentBaseline.md)
- [Deployment of Reference Implementation](/docs/DeploymentReferenceImplementation.md)

## Deployment Steps

1. **Navigate to the teams directory**: Change to the directory containing the Teams application configuration files for the reference implementation deployment.

    ```bash
    cd ./code/teams
    ```

2. **Update the manifest.json**: Open the `manifest.json` file and update the following fields to match your deployment:

    | Property                                 | Description |
    |------------------------------------------|-------------|
    | `id`                                     | Replace the value with the `Microsoft App ID` of your Azure Bot which you can find in the Azure Portal by opening your `Azure Bot` -> `Settings` -> `Configuration` -> `Microsoft App ID`. Teh value is a GUID. |
    | `copilotAgents.customEngineAgents[0].id` | Must the the same value as the `id`. |
    | `bots[0].botId`                          | Must the the same value as the `id`. |
    | `validDomains`                           | Replace with the domain of your web app which you can find in the Azure Portal by opening your `Azure Bot` -> `Settings` -> `Configuration` -> `Messaging endpoint`. The value must have the following format: `https://<your-webapp-name>.azurewebsites.net/api/v1/messages/message`. |

3. **Package the Teams App**: Create a ZIP package of the Teams app by zipping the contents of the directory, including the updated `manifest.json`, `color.png`, and `outline.png` files.

    ```bash
    zip -r manifest.zip .
    ```

4. **Upload the Teams App**:
   - Open Microsoft Teams.
   - Navigate to the "Apps" section.
   - Click on "Upload a custom app" and select "Upload for [Your Team]" or "Upload for me or my teams" based on your preference.
   - Select the `teams-app.zip` file you created in the previous step.

5. **Test the Teams App**: Once the app is uploaded, you can add it to a team or chat and start interacting with the Agent through the Teams interface.

6. **Agent Testing**: Test the functionality of the Agent by sending messages and commands to ensure it responds as expected. Verify that it can access the necessary resources and perform actions defined in the reference implementation.

## Next Steps

With the Teams app deployed, you can now start using the Microsoft 365 Custom Agent within Microsoft Teams. Explore the capabilities of the agent and customize its behavior as needed to fit your organization's requirements.
