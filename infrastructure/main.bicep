targetScope = 'subscription'

@description('Environment name')
@allowed(['dev', 'prod'])
param environment string

@description('Azure region')
param location string = 'eastus2'

@description('SQL admin password')
@secure()
param sqlAdminPassword string

var resourceGroupName = 'meridian-${environment}'
var tags = {
  project: 'meridian'
  environment: environment
}

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

module keyVault 'modules/keyvault.bicep' = {
  name: 'keyvault'
  scope: rg
  params: {
    location: location
    environment: environment
    tags: tags
  }
}

module sql 'modules/sql.bicep' = {
  name: 'sql'
  scope: rg
  params: {
    location: location
    environment: environment
    adminPassword: sqlAdminPassword
    keyVaultName: keyVault.outputs.keyVaultName
    tags: tags
  }
}

module cosmos 'modules/cosmos.bicep' = {
  name: 'cosmos'
  scope: rg
  params: {
    location: location
    environment: environment
    keyVaultName: keyVault.outputs.keyVaultName
    tags: tags
  }
}

module containerApps 'modules/container-apps.bicep' = {
  name: 'container-apps'
  scope: rg
  params: {
    location: location
    environment: environment
    tags: tags
  }
}

output resourceGroupName string = rg.name
output containerAppsEnvironmentId string = containerApps.outputs.environmentId
