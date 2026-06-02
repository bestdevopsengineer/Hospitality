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


choco --version
2.5.0
choco install postgresql --yes

psql --version

Namespace = database environment
Workgroup = compute + endpoint

=============================
SELECT current_database();

CREATE TABLE hotels (
    hotel_id INT,
    hotel_name VARCHAR(100),
    city VARCHAR(100),
    rooms INT
);

INSERT INTO hotels VALUES
(1, 'Luxury Grand Hotel', 'Miami', 250),
(2, 'Royal Beach Resort', 'Orlando', 180);

SELECT * FROM hotels;
hotel_id |     hotel_name     |  city   | rooms
----------+--------------------+---------+-------
1         | Luxury Grand Hotel | Miami   | 250
2         | Royal Beach Resort | Orlando | 180


Terraform
   │
   ├── S3 Backend
   ├── VPC
   ├── Public Subnets
   ├── Internet Gateway
   ├── Route Tables
   ├── Redshift Serverless
   └── EC2 Jump Server
           │
           ▼
AWS Systems Manager
           │
           ▼
Redshift Serverless

# I built a cloud data platform on AWS using Terraform. 
# I provisioned a VPC, networking components, an EC2 jump server, and Redshift Serverless. 
# I configured remote state in S3 with DynamoDB locking, integrated deployments through GitHub Actions using OIDC authentication, secured access with IAM roles and # AWS Systems Manager instead of SSH, and validated the platform by connecting to Redshift from a private EC2 instance and creating/querying tables.