terraform {
  backend "s3" {
    bucket         = "hospitality-terraform-state-502845302465"
    key            = "dev/redshift/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "hospitality-terraform-locks"
  }
}