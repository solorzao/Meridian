param location string
param environment string
param tags object
param containerAppsEnvironmentId string
param registryLoginServer string
param registryName string

// Frontend Container App
resource frontendApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'meridian-frontend'
  location: location
  tags: tags
  properties: {
    managedEnvironmentId: containerAppsEnvironmentId
    configuration: {
      ingress: {
        external: true
        targetPort: 3000
        transport: 'http'
      }
      registries: [
        {
          server: registryLoginServer
          username: registryName
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        {
          name: 'acr-password'
          value: '' // Set during deployment
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'frontend'
          image: '${registryLoginServer}/meridian-frontend:latest'
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          env: [
            { name: 'NEXT_PUBLIC_API_URL', value: 'https://meridian-api.${environment}.azurecontainerapps.io' }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 3
        rules: [
          {
            name: 'http-scale'
            http: { metadata: { concurrentRequests: '50' } }
          }
        ]
      }
    }
  }
}

// API Container App
resource apiApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'meridian-api'
  location: location
  tags: tags
  properties: {
    managedEnvironmentId: containerAppsEnvironmentId
    configuration: {
      ingress: {
        external: true
        targetPort: 8080
        transport: 'http'
      }
      registries: [
        {
          server: registryLoginServer
          username: registryName
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        {
          name: 'acr-password'
          value: ''
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: '${registryLoginServer}/meridian-api:latest'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 5
        rules: [
          {
            name: 'http-scale'
            http: { metadata: { concurrentRequests: '30' } }
          }
        ]
      }
    }
  }
}

// Python Service Container App
resource pythonApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'meridian-python'
  location: location
  tags: tags
  properties: {
    managedEnvironmentId: containerAppsEnvironmentId
    configuration: {
      ingress: {
        external: false
        targetPort: 8000
        transport: 'http'
      }
      registries: [
        {
          server: registryLoginServer
          username: registryName
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        {
          name: 'acr-password'
          value: ''
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'python'
          image: '${registryLoginServer}/meridian-python:latest'
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 3
        rules: [
          {
            name: 'http-scale'
            http: { metadata: { concurrentRequests: '20' } }
          }
        ]
      }
    }
  }
}

output frontendUrl string = 'https://${frontendApp.properties.configuration.ingress.fqdn}'
output apiUrl string = 'https://${apiApp.properties.configuration.ingress.fqdn}'
