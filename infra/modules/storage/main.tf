variable "resource_group_name" {
  description = "Name of the Resource Group"
  type        = string
}

variable "location" {
  description = "Azure Region"
  type        = string
}

variable "storage_account_name" {
  description = "Name of the Storage Account (must be globally unique)"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID for the Private Endpoint"
  type        = string
}

resource "azurerm_storage_account" "adls" {
  name                     = var.storage_account_name
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = true # Critical for ADLS Gen 2 (Hierarchical Namespace)

  network_rules {
    default_action = "Deny"
    bypass         = ["AzureServices"]
  }

  tags = {
    environment = "dev"
    project     = "nexus"
  }
}

# Create Data Lake File Systems (Containers) for Medallion Architecture
resource "azurerm_storage_data_lake_gen2_filesystem" "bronze" {
  name               = "bronze"
  storage_account_id = azurerm_storage_account.adls.id
}

resource "azurerm_storage_data_lake_gen2_filesystem" "silver" {
  name               = "silver"
  storage_account_id = azurerm_storage_account.adls.id
}

resource "azurerm_storage_data_lake_gen2_filesystem" "gold" {
  name               = "gold"
  storage_account_id = azurerm_storage_account.adls.id
}

# Private Endpoint (Security Best Practice)
resource "azurerm_private_endpoint" "adls_pe" {
  name                = "${var.storage_account_name}-pe"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.subnet_id

  private_service_connection {
    name                           = "${var.storage_account_name}-privatelink"
    private_connection_resource_id = azurerm_storage_account.adls.id
    subresource_names              = ["dfs"] # DFS = Data Lake endpoint
    is_manual_connection           = false
  }
}

output "storage_account_id" {
  value = azurerm_storage_account.adls.id
}

output "primary_dfs_endpoint" {
  value = azurerm_storage_account.adls.primary_dfs_endpoint
}
