terraform {
  backend "s3" {
    bucket = "hospitality-terraform-state-502845302465"
    key    = "dev/hospitality/terraform.tfstate"
    region = "us-east-1"
  }
}