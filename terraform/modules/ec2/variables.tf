variable "environment" {
  type = string
}

variable "project_name" {
  type    = string
  default = "hospitality-data-platform"
}

variable "vpc_id" {
  type = string
}

variable "subnet_id" {
  type = string
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}