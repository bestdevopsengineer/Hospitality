resource "aws_glue_catalog_database" "this" {
  name = "${var.environment}_hospitality_catalog"
}

resource "aws_iam_role" "glue" {
  name = "${var.environment}-glue-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "glue.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "glue_service" {
  role       = aws_iam_role.glue.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_iam_role_policy" "glue_s3_access" {
  name = "${var.environment}-glue-s3-access"
  role = aws_iam_role.glue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.data_bucket_name}",
          "arn:aws:s3:::${var.data_bucket_name}/*"
        ]
      }
    ]
  })
}

resource "aws_glue_crawler" "salesforce_raw" {
  name          = "${var.environment}-salesforce-raw-crawler"
  role          = aws_iam_role.glue.arn
  database_name = aws_glue_catalog_database.this.name

  s3_target {
    path = "s3://${var.data_bucket_name}/raw/salesforce/"
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}