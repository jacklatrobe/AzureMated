# Azure Test Data Source Environment

This guide explains how to deploy a small Azure environment for testing AzureMated. The deployment is driven by a Bicep template that creates a resource group and common data resources.

## Prerequisites

- Azure CLI (or Azure Developer CLI)
- Access to an Azure subscription
- Permission to create resources in the subscription

## Create the Bicep Template

To set up the test environment, we'll create a single Bicep file that deploys all the necessary resources:

1. Create a new file named `test.bicep`.
2. Copy the following code into the file:

```bicep
// Single Bicep file for Resource Group and Resources
targetScope = 'resourceGroup'

// Parameters
param location string = 'eastus'
param ownerTagValue string = 'AzureMated'  // Required by policy
param storageBlobAccountName string = 'ffblob${uniqueString(resourceGroup().id)}'
param storageAdlsAccountName string = 'ffadls${uniqueString(resourceGroup().id)}'
param sqlServerName string = 'ffsql${uniqueString(resourceGroup().id)}'
param sqlAdminUser string = 'sqladminuser'
@secure()
param sqlAdminPassword string
param sqlDbName string = 'ffdb'
param dataFactoryName string = 'ffadf${uniqueString(resourceGroup().id)}'
param fabricName string = 'fffabric${uniqueString(resourceGroup().id)}'

// Storage account for Blob storage
resource storageBlob 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: storageBlobAccountName
  location: location
  tags: {
    Owner: ownerTagValue
  }
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {}
}

// Storage account for ADLS
resource storageAdls 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: storageAdlsAccountName
  location: location
  tags: {
    Owner: ownerTagValue
  }
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    isHnsEnabled: true
  }
}

// SQL Server instance
resource sqlServer 'Microsoft.Sql/servers@2022-05-01-preview' = {
  name: sqlServerName
  location: location
  tags: {
    Owner: ownerTagValue
  }
  properties: {
    administratorLogin: sqlAdminUser
    administratorLoginPassword: sqlAdminPassword
  }
}

// Allow Azure services to access the SQL server
resource sqlServerFirewallRule 'Microsoft.Sql/servers/firewallRules@2022-05-01-preview' = {
  parent: sqlServer
  name: 'AllowAllAzureIPs'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// SQL Database
resource sqlDb 'Microsoft.Sql/servers/databases@2022-05-01-preview' = {
  parent: sqlServer
  name: sqlDbName
  location: location
  tags: {
    Owner: ownerTagValue
  }
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
}

// Data Factory instance
resource dataFactory 'Microsoft.DataFactory/factories@2018-06-01' = {
  name: dataFactoryName
  location: location
  tags: {
    Owner: ownerTagValue
  }
  identity: {
    type: 'SystemAssigned'
  }
}

// Fabric instance
resource fabricInstance 'Microsoft.Fabric/capacities@2023-11-01' = {
  name: fabricName
  location: location
  tags: {
    Owner: ownerTagValue
  }
  sku: {
    name: 'F0'
    tier: 'Fabric'
  }
  properties: {
    administration: {
      members: [
        'user@contoso.com'  // Replace with your Azure AD user principal
      ]
    }
  }
}
```

3. You MUST set a valid Fabric capacity administrator - replace user@contoso.com
3. Save the file.

## Deploy the Template

If you need to create a new resource group:

```bash
az group create --name <resource-group-name> --location <azure-region> --tags Owner=AzureMated
```

Note: The Owner tag may be required by policy for resources and groups.

Then deploy the template to the resource group:

```bash
az deployment group create \
  --resource-group <resource-group-name> \
  --template-file test.bicep \
  --parameters sqlAdminPassword=<password>
```

Replace `<azure-region>` with your preferred region (e.g., 'eastus', 'westus', 'australiaeast') without any underscores, hyphens or spaces. For example, use 'australiaeast' not 'australia_east' or 'australia-east'. Replace `<resource-group-name>` with the desired name (resource group names can contain hyphens and underscores). Use a secure password for the SQL administrator login.

## Next Steps

The created resources can be used as data sources for AzureMated modules. Update your configuration to reference the storage accounts, SQL Database, Data Factory, and Fabric capacity as needed.

## See Also

- [Getting Started](getting-started.md)
- [Architecture Overview](architecture.md)
