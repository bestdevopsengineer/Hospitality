data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_instance" "jump_server" {
  ami                  = data.aws_ami.amazon_linux.id
  instance_type        = var.instance_type
  subnet_id            = var.subnet_id
  iam_instance_profile = aws_iam_instance_profile.ssm.name


  tags = {
    Name        = "${var.environment}-jump-server"
    Environment = var.environment
    Project     = var.project_name
  }
}