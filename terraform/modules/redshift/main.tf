variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "hospitality-data-platform"
}

variable "subnet_ids" {
  description = "Private subnet IDs for Redshift"
  type        = list(string)
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}