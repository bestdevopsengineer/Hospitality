# Hospitality
terraform -chdir=terraform/components/s3 init
terraform -chdir=terraform/components/s3 plan -var="environment=dev"