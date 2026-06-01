resource "aws_redshift_subnet_group" "this" {
  name       = "${var.environment}-redshift-subnet-group"
  subnet_ids = var.subnet_ids


  tags = {
    Name        = "${var.environment}-redshift-subnet-group"
    Environment = var.environment
    Project     = var.project_name
  }
}

# resource "aws_redshift_cluster" "this" {
#   cluster_identifier = "${var.environment}-redshift"

#   database_name   = "hospitality"
#   master_username = "adminuser"
#   master_password = var.master_password

#   node_type    = "ra3.xlplus"
#   cluster_type = "single-node"

#   cluster_subnet_group_name = aws_redshift_subnet_group.this.name

#   publicly_accessible  = false
#   encrypted            = true
#   enhanced_vpc_routing = true

#   skip_final_snapshot = true
# }

resource "aws_redshiftserverless_namespace" "this" {
  namespace_name = coalesce(var.namespace_name, "${var.environment}-hospitality-namespace")

  db_name             = "hospitality"
  admin_username      = "adminuser"
  admin_user_password = var.master_password

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_redshiftserverless_workgroup" "this" {
  workgroup_name = coalesce(var.workgroup_name, "${var.environment}-hospitality-workgroup")

  namespace_name = aws_redshiftserverless_namespace.this.namespace_name
  subnet_ids     = var.subnet_ids

  security_group_ids  = [aws_security_group.redshift.id]
  publicly_accessible = false

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}