resource "aws_redshift_subnet_group" "this" {
  name       = "${var.environment}-redshift-subnet-group"
  subnet_ids = var.subnet_ids

  tags = {
    Name        = "${var.environment}-redshift-subnet-group"
    Environment = var.environment
    Project     = var.project_name
  }
}