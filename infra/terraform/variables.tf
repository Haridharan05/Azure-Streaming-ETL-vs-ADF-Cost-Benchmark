variable "prefix" {
  description = "Name prefix for all resources"
  type        = string
  default     = "etlbench"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus"
}