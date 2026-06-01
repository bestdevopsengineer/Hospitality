data "terraform_remote_state" "networking" {
  backend = "s3"

  config = {
    bucket = "hospitality-terraform-state-502845302465"
    key    = "dev/networking/terraform.tfstate"
    region = "us-east-1"
  }
}

module "ec2" {
  source = "../../modules/ec2"

  environment = var.environment
  vpc_id      = data.terraform_remote_state.networking.outputs.vpc_id
  subnet_id   = data.terraform_remote_state.networking.outputs.public_subnet_ids[0]
}