# Azure Test Data Source Environment

This guide explains how to deploy a small Azure environment for testing FabricFriend. The deployment is driven by a Bicep template that creates a resource group and common data resources.

## Prerequisites

- Azure CLI (or Azure Developer CLI)
- Access to an Azure subscription
- Permission to create resources in the subscription

## Create the Bicep Template

1. Create a new file named `test-environment.bicep`.
2. Copy the following code into the file:

```bicep
targetScope = 'subscription'

param location string = 'eastus'
param rgName string = 'ff-test-rg'
param storageBlobAccountName string = 'ffblob${uniqueString(rgName)}'
param storageAdlsAccountName string = 'ffadls${uniqueString(rgName)}'
param sqlServerName string = 'ffsql${uniqueString(rgName)}'
param sqlAdminUser string = 'sqladminuser'
@secure()
param sqlAdminPassword string
param sqlDbName string = 'ffdb'
param dataFactoryName string = 'ffadf${uniqueString(rgName)}'
param fabricName string = 'fffabric${uniqueString(rgName)}'

resource rg 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: rgName
  location: location
}

resource storageBlob 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: storageBlobAccountName
  location: rg.location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {}
}

resource storageAdls 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: storageAdlsAccountName
  location: rg.location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    isHnsEnabled: true
  }
}

resource sqlServer 'Microsoft.Sql/servers@2022-05-01-preview' = {
  name: sqlServerName
  location: rg.location
  properties: {
    administratorLogin: sqlAdminUser
    administratorLoginPassword: sqlAdminPassword
  }
}

resource sqlDb 'Microsoft.Sql/servers/databases@2022-05-01-preview' = {
  parent: sqlServer
  name: sqlDbName
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
}

resource dataFactory 'Microsoft.DataFactory/factories@2018-06-01' = {
  name: dataFactoryName
  location: rg.location
}

resource fabricInstance 'Microsoft.PowerBIDedicated/capacities@2023-01-01' = {
  name: fabricName
  location: rg.location
  sku: {
    name: 'F0'
  }
}
```

3. Save the file.

## Deploy the Template

Run the following command, providing a location and resource group name. If the resource group does not exist, it will be created automatically.

```bash
az deployment sub create \
  --location <azure-region> \
  --template-file test-environment.bicep \
  --parameters rgName=<resource-group-name> sqlAdminPassword=<password>
```

Replace `<azure-region>` with your preferred region and `<resource-group-name>` with the desired name. Use a secure password for the SQL administrator login.

## Next Steps

The created resources can be used as data sources for FabricFriend modules. Update your configuration to reference the storage accounts, SQL Database, Data Factory, and Fabric capacity as needed.

## See Also

- [Getting Started](getting-started.md)
- [Architecture Overview](architecture.md)
