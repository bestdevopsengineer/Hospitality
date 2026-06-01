resource "aws_redshift_subnet_group" "this" {
  name       = "${var.environment}-redshift-subnet-group"
  subnet_ids = var.subnet_ids


  tags = {
    Name        = "${var.environment}-redshift-subnet-group"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_redshift_cluster" "this" {
  cluster_identifier = "${var.environment}-redshift"

  database_name   = "hospitality"
  master_username = "adminuser"
  master_password = var.master_password

  node_type    = "dc2.large"
  cluster_type = "single-node"

  cluster_subnet_group_name = aws_redshift_subnet_group.this.name

  publicly_accessible  = false
  encrypted            = true
  enhanced_vpc_routing = true

  skip_final_snapshot = true
}