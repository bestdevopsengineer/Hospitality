Step 1: Create a new Salesforce test CSV

# salesforce_accounts.csv
account_id,account_name,industry,city,state,annual_revenue
A001,Luxury Grand Hotel,Hospitality,Miami,FL,25000000
A002,Royal Beach Resort,Hospitality,Orlando,FL,18000000
A003,Mountain View Lodge,Hospitality,Denver,CO,9000000
A004,Ocean Breeze Resort,Hospitality,San Diego,CA,32000000

# salesforce_accounts_update.csv
account_id,account_name,industry,city,state,annual_revenue
A001,Luxury Grand Hotel,Hospitality,Miami,FL,30000000
A002,Royal Beach Resort,Hospitality,Orlando,FL,18000000
A003,Mountain View Lodge,Hospitality,Denver,CO,9500000
A004,Ocean Breeze Resort,Hospitality,San Diego,CA,32000000
A005,Desert Star Hotel,Hospitality,Phoenix,AZ,11000000


# This simulates Salesforce sending:
A001 updated revenue
A003 updated revenue
A005 new account

# Step 2: upload the update file to S3.
aws s3 cp salesforce_accounts_update.csv \
s3://luxury-data-platform-dev-12345/raw/salesforce/accounts/salesforce_accounts_update.csv \
--region us-east-1

# Then check Lambda logs:
MSYS_NO_PATHCONV=1 aws logs tail /aws/lambda/dev-s3-redshift-loader \
  --region us-east-1 \
  --since 5m

 # Look for:
  Statement status: FINISHED

SELECT COUNT(*)
FROM salesforce_accounts;