module "s3_event_loader" {
  source = "../../modules/lambda"

  environment    = var.environment
  function_name  = "s3-redshift-loader"
  s3_bucket_name = "luxury-data-platform-${var.environment}-12345"
}