data "terraform_remote_state" "networking" {
  backend = "s3"

  config = {
    bucket = "hospitality-terraform-state-502845302465"
    key    = "dev/networking/terraform.tfstate"
    region = "us-east-1"
  }
}

module "redshift" {
  source = "../../modules/redshift"

  environment = var.environment
  vpc_id      = data.terraform_remote_state.networking.outputs.vpc_id
  subnet_ids  = data.terraform_remote_state.networking.outputs.private_subnet_ids
}