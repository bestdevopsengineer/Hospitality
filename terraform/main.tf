resource "aws_s3_bucket" "data_bucket" {
  bucket = "luxury-data-platform-${var.environment}-12345"

  tags = {
    Name        = "Luxury Data Platform"
    Environment = var.environment
  }
}