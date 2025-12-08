**Archived Branch**

# Azure AI Bot Assistant Reference Implementation

![Icon](/docs/images/icon.png)

In this repository, it is shown how to build an easy to maintain RAG solution based on Bot Framework and Azure Open AI Assistant. The benefits provided by this solution are:

- **Multi-channel support:** Easy and simple integration into various channels like Microsoft Teams, Microsoft Outlook, Slack, Telegram, Email, Web Chat and [many others](https://learn.microsoft.com/en-us/azure/bot-service/bot-service-manage-channels?view=azure-bot-service-4.0#channels-list).
- **Much reduced management overhead:** Much reduced infrastructure footprint and management overhead since user thread state management and vector databases are managed internally.
- **Secure-by-default & Compliance-by-design:** This reference implementation was build for enterprise customers and provides a secure baseline for networking, identity, encryption, logging & monitoring and more.
-  **Basics solved out of the box:** This reference implementation solves common application aspects like logging & monitoring, authentication & authorization, infrastrcuture as code and much more out of the box and is ready to be used for larger implementations.

## Architecture

![Architecture](/docs/images/architecture.png)

The architecture consists of:

- An *ingestion-layer* and
- a *concumption-layer*.

### Ingestion-layer

The ingestion-layer is responsible for integrating data from various data sources into the application environment. Azure Data Factory is being used here as it offers a large number of connectors that can be used easily to integrate data from many different data sources within the corporate network and outside. A storage account is deployed is a separate resource group and can be used by Azure Data Factory to store the ingested data. An additional Azure Function is being introduced in the ingest layer to be able to extract additional metadata from images and other unstructured data from the respective data sources that have been ingested using Azure Data Factory. In addition, the Azure Function can be used to convert data into a data format that is supported by the [File Search feature](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/file-search?tabs=python#supported-file-types) of Azure Open AI Assisstants. A Key Vault is deployed to store secrets for Azure Data Factory or the Azure Function to connect to data sources or other external services.

### Consumption-layer

The consumption-layer is responsible for serving live-traffic from users submitting messages and queries through one of the supported channels. Azure Bot Framework is being used as an orchestration-layer in the consumption-layer and handles the authentication of users as well as the interaction of the users with the Azure Open AI Assistant. A Cosmos DB is being used to store relevant information per user like the `thread-id` or `vector-store-id` that is assigned to them and that contains the user context. The actual user thread management as well as the vector store management is fully handed over to the Azure Open AI assistant API. A Key Vault is deployed to be able to store secrets for the Azure Web App in a secure place. Application Insights is deployed for logging and monitoring. Additional Azure Dashboards or Azure Alerts may be included in the future.

## Azure Open AI Assistant Vectore Stores

Azure Open AI Assistant API supports teh following vector stores:

1. A global vector store at the assistant level and
2. A dedicated vectore store for each thread.

### Global Vector Store

The global vector store is being used by the ingestion-layer to enable common chat on your data scenarios for all users interacting with the consumption-layer. This vector store should only be used for data assets that should be visible to all users as you cannot define granular access permissions within the vectore store.

### Thread Vector Store

The thread vector store should be used to store user-specific data. In the current solution, the thread vector store is used when users upload data and files to the channel. The data is then being added to the thread vector store in the background to enable chat on your data scenarios for these new data assets.
