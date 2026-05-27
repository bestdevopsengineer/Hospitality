resource "aws_s3_bucket" "data_bucket" {
  bucket = "luxury-data-platform-demo-12345"

  tags = {
    Name        = "Luxury Data Platform"
    Environment = "dev"
  }
}