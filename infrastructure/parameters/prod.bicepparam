using '../main.bicep'

param environment = 'prod'
param location = 'eastus2'
param sqlAdminPassword = '' // Set via CLI or pipeline
