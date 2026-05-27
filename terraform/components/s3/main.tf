module "data_bucket" {
  source = "../../modules/s3-bucket"

  bucket_name = "luxury-data-platform-dev-12345"
  environment = var.environment
}

module "logs_bucket" {
  source = "../../modules/s3-bucket"

  bucket_name = "luxury-data-platform-${var.environment}-logs-12345"
  environment = var.environment
}