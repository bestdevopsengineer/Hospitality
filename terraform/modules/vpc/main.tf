resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.environment}-hospitality-vpc"
    Environment = var.environment
    Project     = var.project_name
  }
}