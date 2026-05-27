fmt → validate → security scan → plan → approval → merge → apply

# Hospitality
terraform -chdir=terraform/components/s3 init
terraform -chdir=terraform/components/s3 plan -var="environment=dev"

You now built:

reusable Terraform modules
component-based infrastructure
isolated remote state
GitHub Actions CI/CD
OIDC AWS authentication
environment-aware deployments
PR validation workflow

# Delete one resource

Remove or comment that resource from code.

module "logs_bucket" {
  source = "../../modules/s3-bucket"

  bucket_name = "luxury-data-platform-${var.environment}-logs-12345"
  environment = var.environment
}
Then run:
terraform -chdir=terraform/components/s3 plan -var="environment=dev"

# Delete all resources in that component
terraform -chdir=terraform/components/s3 destroy -var="environment=dev"
This deletes everything managed by:
dev/s3/terraform.tfstate

What is still missing for full enterprise flow:

monitoring
rollback automation
notifications
manual production approval gates
plan artifacts/comments
state locking
security scanning

Your next maturity levels would be:

1. Networking/VPC modules
2. EC2/EKS/Redshift components
3. DynamoDB locking
4. Terraform reusable workflows
5. Slack/Teams notifications
6. CloudWatch monitoring
7. Rollback strategy
8. Drift detection
9. Security scanning (Checkov/tfsec)
10. Terraform plan comments on PRs

# create a DynamoDB table manually in AWS:
Table name: hospitality-terraform-locks
Partition key: LockID
Type: String
# 