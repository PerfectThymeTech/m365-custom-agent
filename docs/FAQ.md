# FAQ

### In which regions do you recommend deploying your services?

We recommend deploying your services in regions that are geographically close to your user base to minimize latency. Additionally, consider regions that support all the Azure services you plan to use. Today, we recommend using GPT 5.1 for the custom agent. The model is only available in select Azure regions. You can find a list of supported regions in [the Azure documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-models/concepts/models-sold-directly-by-azure?view=foundry-classic&tabs=global-standard-aoai%2Cstandard-chat-completions%2Cglobal-standard&pivots=azure-openai#gpt-51).

In addition, we have seen quota issues in some regions for services like Azure App Service Plan, so it's important to ensure that the region you choose has sufficient quota for the services you plan to use. You can check your current quotas and request increases through the Azure portal.
