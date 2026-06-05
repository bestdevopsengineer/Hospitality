module "glue" {
  source = "../../modules/glue"

  environment      = var.environment
  data_bucket_name = "luxury-data-platform-${var.environment}-12345"
}