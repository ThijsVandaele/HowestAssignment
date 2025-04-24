# Load environment variables from .env file
$envFilePath = ".\.env"
$envVars = @{}
Get-Content $envFilePath | ForEach-Object {
    if ($_ -match "^(.*?)=(.*)$") {
        $envVars[$matches[1]] = $matches[2]
    }
}

# Assign variables from the .env file to PowerShell variables
$resourceGroup = $envVars["RESOURCE_GROUP"]
$location = $envVars["LOCATION"]
$environmentName = $envVars["ENVIRONMENT_NAME"]

$registryName = $envVars["REGISTRY_NAME"]
$registryServerName = "$registryUserName.azurecr.io"

$appApiName = $envVars["APP_API_NAME"]
$appDbName = $envVars["APP_DB_NAME"]
$appDbPort = $envVars["APP_DB_PORT"]

$dbUser = $envVars["DB_USER"]
$dbPassword = $envVars["DB_PASSWORD"]
$dbName = $envVars["DB_NAME"]
$dbServerRootPassword = $envVars["DB_ROOTPASSWORD"]

# LOGIN 
az login

# Create ResourceGroup
az group create --name $resourceGroup --location $location

# Create Registry
az acr create --resource-group $resourceGroup --name $registryName --sku Basic
az acr login --name $registryName
# Enable the admin user if not already enabled
az acr update --name $registryName --admin-enabled true

# Get the ACR admin username and password
$acrCredentials = az acr credential show --name $registryName | ConvertFrom-Json
$registryUsername = $acrCredentials.username
$registryPassword = $acrCredentials.passwords[0].value

# Build/push/tag to registry
$mariaDbBaseImageTag='mariadb:latest'
docker pull $mariaDbBaseImageTag
$tagNameDb = "$registryServerName/$appDbName"
docker tag $mariaDbBaseImageTag $tagNameDb
docker push $tagNameDb

$tagName = "$registryServerName/$appApiName"
docker build .\todo-api\ -t $tagName
docker push $tagName

# Create Azure Container Environment
az containerapp env create `
    --name $environmentName `
    --resource-group $resourceGroup `
    --location $location

# Create Azure Container App MariaDb
az containerapp create `
    --name $appDbName `
    --resource-group $resourceGroup `
    --environment $environmentName `
    --image docker.io/mariadb `
    --env-vars MYSQL_ROOT_PASSWORD=$dbServerRootPassword `
                MYSQL_DATABASE=$dbName `
                MYSQL_USER=$dbUser `
                MYSQL_PASSWORD=$dbPassword `
    --target-port appDbPort `
    --ingress internal `
    --transport tcp

# Create Azure Container App API 
az containerapp create `
    --name $appApiName `
    --resource-group $resourceGroup `
    --environment $environmentName `
    --image $tagName `
    --registry-server $registryServerName `
    --registry-password $registryPassword `
    --registry-username $registryUsername `
    --target-port 80 `
    --ingress external `
    --env-vars DB_USER=$dbUser `
                DB_PASSWORD=$dbPassword `
                DB_NAME=$dbName `
                DB_HOST=$appDbName  `
                DB_PORT=$appDbPort

az containerapp update `
  --name $appApiName `
  --resource-group $resourceGroup `
  --set template.containers[0].livenessProbe.type="Http" `
  --set template.containers[0].livenessProbe.httpGet.path="/healthz" `
  --set template.containers[0].readinessProbe.type="Http" `
  --set template.containers[0].readinessProbe.httpGet.path="/readiness"
