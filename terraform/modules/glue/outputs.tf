output "glue_database_name" {
  value = aws_glue_catalog_database.this.name
}

output "glue_crawler_name" {
  value = aws_glue_crawler.salesforce_raw.name
}

output "glue_role_arn" {
  value = aws_iam_role.glue.arn
}