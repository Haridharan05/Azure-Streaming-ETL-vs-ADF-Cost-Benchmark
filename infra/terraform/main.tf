resource "azurerm_resource_group" "rg" {
  name     = "${var.prefix}-rg"
  location = var.location
}

resource "azurerm_service_plan" "plan" {
  name                = "${var.prefix}-plan"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku_name            = "B1"
}

resource "azurerm_linux_web_app" "app" {
  name                = "${var.prefix}-app"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  service_plan_id     = azurerm_service_plan.plan.id
  https_only          = true

  site_config {
    application_stack {
      python_version = "3.12"
    }
  }

  app_settings = {
    AZ_BLOB_CONN       = azurerm_storage_account.sa.primary_connection_string
    ADLS_URL           = azurerm_storage_account.sa.primary_connection_string
    MYSQL_HOST         = azurerm_mysql_flexible_server.db.fqdn
    MYSQL_USER         = "${azurerm_mysql_flexible_server.db.administrator_login}@${azurerm_mysql_flexible_server.db.name}"
    MYSQL_PWD          = azurerm_mysql_flexible_server.db.administrator_password
    MYSQL_DB           = azurerm_mysql_database.raw.name
  }

  container_registry_use_managed_identity = true
  # Push your image manually or via az acr build
  site_config_linux_fx_version = "DOCKER|<acr>.azurecr.io/etl:latest"
}

resource "azurerm_storage_account" "sa" {
  name                     = "${var.prefix}sa"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true   # ADLS Gen2
}

resource "azurerm_mysql_flexible_server" "db" {
  name                   = "${var.prefix}-mysql"
  resource_group_name    = azurerm_resource_group.rg.name
  location               = azurerm_resource_group.rg.location
  administrator_login    = "mysqladmin"
  administrator_password = random_password.pwd.result
  sku_name               = "B_Standard_B1ms"
  storage_mb             = 32768
  version                = "8.0.21"
}

resource "random_password" "pwd" {
  length  = 16
  special = true
}

resource "azurerm_mysql_database" "raw" {
  name                = "raw"
  resource_group_name = azurerm_resource_group.rg.name
  server_name         = azurerm_mysql_flexible_server.db.name
  charset             = "utf8mb4"
  collation           = "utf8mb4_unicode_ci"
}