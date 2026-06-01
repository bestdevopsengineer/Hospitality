resource "aws_security_group" "redshift" {
  name        = "${var.environment}-redshift-sg"
  description = "Security group for Redshift Serverless"
  vpc_id      = var.vpc_id

  tags = {
    Name        = "${var.environment}-redshift-sg"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_vpc_security_group_ingress_rule" "redshift" {
  security_group_id = aws_security_group.redshift.id

  from_port   = 5439
  to_port     = 5439
  ip_protocol = "tcp"

  cidr_ipv4 = "10.0.0.0/16"
}