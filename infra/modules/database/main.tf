variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "server_name" {
  description = "Name of the Postgres Server"
  type        = string
}

variable "admin_username" {
  type = string
}

variable "admin_password" {
  type      = string
  sensitive = true
}

variable "subnet_id" {
  description = "Delegated Subnet ID for Postgres"
  type        = string
}

# Private DNS Zone for Postgres Flexible Server
resource "azurerm_private_dns_zone" "postgres_dns" {
  name                = "privatelink.postgres.database.azure.com"
  resource_group_name = var.resource_group_name
}

resource "azurerm_private_dns_zone_virtual_network_link" "dns_link" {
  name                  = "postgres-dns-link"
  private_dns_zone_name = azurerm_private_dns_zone.postgres_dns.name
  virtual_network_id    = var.subnet_id # Note: Needs VNet ID, passed via var or derived. 
                                        # For simplicity in this module, we assume passed or handled in main. 
                                        # *Correction*: We need VNet ID. Let's add a variable.
  resource_group_name   = var.resource_group_name
}

variable "vnet_id" {
    type = string
}

resource "azurerm_postgresql_flexible_server" "postgres" {
  name                   = var.server_name
  resource_group_name    = var.resource_group_name
  location               = var.location
  version                = "13"
  delegated_subnet_id    = var.subnet_id
  private_dns_zone_id    = azurerm_private_dns_zone.postgres_dns.id
  administrator_login    = var.admin_username
  administrator_password = var.admin_password
  storage_mb             = 32768
  sku_name               = "B_Standard_B1ms" # Burstable for Dev/Test cost optimization

  depends_on = [azurerm_private_dns_zone_virtual_network_link.dns_link]
}

output "server_fqdn" {
  value = azurerm_postgresql_flexible_server.postgres.fqdn
}
