from enum import Enum


class AuthorizationTypes(str, Enum):
    CLIENT_SECRET = "ClientSecret"
    USER_MANAGED_IDENTITY = "UserManagedIdentity"
    SYSTEM_MANAGED_IDENTITY = "SystemManagedIdentity"
    FEDERATED_CREDENTIALS = "FederatedCredentials"
    WORKLOAD_IDENTITY = "WorkloadIdentity"
