variable "environment" {
  type = string
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "master_password" {
  type      = string
  sensitive = true
}