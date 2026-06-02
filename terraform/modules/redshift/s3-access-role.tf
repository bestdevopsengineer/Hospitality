resource "aws_iam_role" "redshift_s3_access" {
  name = "${var.environment}-redshift-s3-access-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "redshift.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "redshift_s3_access" {
  name = "${var.environment}-redshift-s3-access-policy"
  role = aws_iam_role.redshift_s3_access.id

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
          "arn:aws:s3:::luxury-data-platform-${var.environment}-12345",
          "arn:aws:s3:::luxury-data-platform-${var.environment}-12345/*"
        ]
      }
    ]
  })
}