aws ssm start-session   --target i-03866a693e0b236b9   --region us-east-1
==========
PGPASSWORD='UseSomethingStrong123!' psql   -h dev-hospitality-workgroup.502845302465.us-east-1.redshift-serverless.amazonaws.com   -p 5439   -U adminuser   -d hospitality
===========
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';

 table_name        
--------------------------
 hotels
 salesforce_opportunities
 salesforce_accounts
(3 rows)
=============
# create the staging table:
CREATE TABLE staging_salesforce_accounts
(
    account_id VARCHAR(50),
    account_name VARCHAR(255),
    industry VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(50),
    annual_revenue DECIMAL(18,2)
);

# Next step: grant Lambda permission to load into the staging table.

GRANT INSERT, SELECT, DELETE, UPDATE
ON TABLE staging_salesforce_accounts
TO "IAMR:dev-s3-redshift-loader-role";

=========
load into the staging table:
aws s3 cp salesforce_accounts.csv \
s3://luxury-data-platform-dev-12345/raw/salesforce/accounts/staging-test-accounts.csv \
--region us-east-1

Then check logs:
MSYS_NO_PATHCONV=1 aws logs tail /aws/lambda/dev-s3-redshift-loader \
  --region us-east-1 \
  --since 5m

  # Verify data landed in the staging table:
  SELECT COUNT(*)
FROM staging_salesforce_accounts;

# Next step: run the MERGE/UPSERT into the final table:
MERGE INTO salesforce_accounts
USING staging_salesforce_accounts
ON salesforce_accounts.account_id = staging_salesforce_accounts.account_id
WHEN MATCHED THEN UPDATE SET
    account_name = staging_salesforce_accounts.account_name,
    industry = staging_salesforce_accounts.industry,
    city = staging_salesforce_accounts.city,
    state = staging_salesforce_accounts.state,
    annual_revenue = staging_salesforce_accounts.annual_revenue
WHEN NOT MATCHED THEN INSERT (
    account_id,
    account_name,
    industry,
    city,
    state,
    annual_revenue
)
VALUES (
    staging_salesforce_accounts.account_id,
    staging_salesforce_accounts.account_name,
    staging_salesforce_accounts.industry,
    staging_salesforce_accounts.city,
    staging_salesforce_accounts.state,
    staging_salesforce_accounts.annual_revenue
);

# First confirm duplicates:
SELECT account_id, COUNT(*)
FROM staging_salesforce_accounts
GROUP BY account_id
HAVING COUNT(*) > 1;

# Then clean staging and reload only one copy later:
TRUNCATE TABLE staging_salesforce_accounts;

# send data back to staging_salesforce_accounts

# MERGE again
MERGE INTO salesforce_accounts
USING staging_salesforce_accounts
ON salesforce_accounts.account_id = staging_salesforce_accounts.account_id
WHEN MATCHED THEN UPDATE SET
    account_name = staging_salesforce_accounts.account_name,
    industry = staging_salesforce_accounts.industry,
    city = staging_salesforce_accounts.city,
    state = staging_salesforce_accounts.state,
    annual_revenue = staging_salesforce_accounts.annual_revenue
WHEN NOT MATCHED THEN INSERT (
    account_id,
    account_name,
    industry,
    city,
    state,
    annual_revenue
)
VALUES (
    staging_salesforce_accounts.account_id,
    staging_salesforce_accounts.account_name,
    staging_salesforce_accounts.industry,
    staging_salesforce_accounts.city,
    staging_salesforce_accounts.state,
    staging_salesforce_accounts.annual_revenue
);

SELECT COUNT(*) FROM salesforce_accounts;

# To see the duplicates, run:
SELECT account_id, COUNT(*)
FROM salesforce_accounts
GROUP BY account_id
HAVING COUNT(*) > 1;

# Next clean it safely:
CREATE TABLE salesforce_accounts_clean AS
SELECT DISTINCT *
FROM salesforce_accounts;

# Then replace the old table:
DROP TABLE salesforce_accounts;

ALTER TABLE salesforce_accounts_clean
RENAME TO salesforce_accounts;

# Then verify:
SELECT account_id, COUNT(*)
FROM salesforce_accounts
GROUP BY account_id
HAVING COUNT(*) > 1;


SELECT COUNT(*) FROM salesforce_accounts;

# After the MERGE succeeds, so it is ready for the next Salesforce file. run:
TRUNCATE TABLE staging_salesforce_accounts;

Salesforce file #1
      ↓
Load staging
      ↓
MERGE
      ↓
TRUNCATE staging

Salesforce file #2
      ↓
Load staging
      ↓
MERGE
      ↓
TRUNCATE staging

This prevents:

duplicate staging data
larger MERGE operations
unnecessary storage usage

SELECT COUNT(*)
FROM staging_salesforce_accounts;


So the final pipeline becomes fully automated:
Salesforce CSV
   ↓
S3
   ↓
Lambda
   ↓
staging table
   ↓
MERGE/UPSERT
   ↓
final table
   ↓
clean staging

aws s3 cp salesforce_accounts.csv \
s3://luxury-data-platform-dev-12345/raw/salesforce/accounts/full-pipeline-test.csv \
--region us-east-1

Then check logs:
MSYS_NO_PATHCONV=1 aws logs tail /aws/lambda/dev-s3-redshift-loader \
  --region us-east-1 \
  --since 5m

S3
 ↓
Lambda
 ↓
COPY staging
 ↓
MERGE final
 ↓
TRUNCATE staging
 ↓
FINISHED
  # Next step, run this in Redshift:
    GRANT SELECT, INSERT, UPDATE, DELETE
    ON TABLE salesforce_accounts
    TO "IAMR:dev-s3-redshift-loader-role";

aws s3 cp salesforce_accounts.csv \
s3://luxury-data-platform-dev-12345/raw/salesforce/accounts/full-pipeline-test-2.csv \
--region us-east-1

GRANT INSERT, SELECT, DELETE, UPDATE
ON TABLE staging_salesforce_accounts
TO "IAMR:dev-s3-redshift-loader-role";

SELECT grantee,
       privilege_type
FROM information_schema.role_table_grants
WHERE table_name = 'staging_salesforce_accounts';

# Let's verify who owns the staging table.
SELECT tablename,
       tableowner
FROM pg_tables
WHERE tablename = 'staging_salesforce_accounts';

aws s3 cp salesforce_accounts.csv \
s3://luxury-data-platform-dev-12345/raw/salesforce/accounts/full-pipeline-test-4.csv \
--region us-east-1

MSYS_NO_PATHCONV=1 aws logs tail /aws/lambda/dev-s3-redshift-loader \
  --region us-east-1 \
  --since 5m

SELECT usename
FROM pg_user
ORDER BY usename;

GRANT ALL PRIVILEGES
ON TABLE staging_salesforce_accounts
TO "IAMR:dev-s3-redshift-loader-role";

GRANT ALL PRIVILEGES
ON TABLE salesforce_accounts
TO "IAMR:dev-s3-redshift-loader-role";

aws s3 cp salesforce_accounts.csv \
s3://luxury-data-platform-dev-12345/raw/salesforce/accounts/full-pipeline-test-5.csv \
--region us-east-1

MSYS_NO_PATHCONV=1 aws logs tail /aws/lambda/dev-s3-redshift-loader \
  --region us-east-1 \
  --since 5m

  Salesforce
    ↓
(EventBridge schedule or API extraction)
    ↓
Lambda Extract
    ↓
S3 Raw Bucket
    ↓
S3 Event Notification
    ↓
Lambda Loader
    ↓
COPY → staging_salesforce_accounts
    ↓
MERGE / UPSERT
    ↓
salesforce_accounts
    ↓
TRUNCATE staging
    ↓
Analysts query Redshift

# And the AWS services involved:
Salesforce
EventBridge
Lambda
S3
IAM
Redshift Serverless
Redshift Data API
CloudWatch
Terraform
GitHub Actions

📤 Salesforce
      │
      ▼
⏰ EventBridge (schedule) 
or  
🔌 API Extraction
      │
      ▼
🧩 Lambda Extract
📄 Pulls data via Bulk API / REST
      │
      ▼
🪣 S3 Raw Bucket (RAW Zone)
📁 Stores untouched CSV/JSON
      │
      ▼
🔔 S3 Event Notification
Triggers next step
      │
      ▼
🧩 Lambda Loader
📝 Prepares COPY command
      │
      ▼
🛢️ Redshift (Staging)
📥 COPY → staging_salesforce_accounts
      │
      ▼
🔄 MERGE / UPSERT
Updates final table with new + changed records
      │
      ▼
🛢️ Redshift (Final Table)
📊 salesforce_accounts
      │
      ▼
🧹 TRUNCATE staging
Clean up temporary data
      │
      ▼
📈 Analysts / BI Tools
Power BI, Tableau, Looker query Redshift

⭐ All the Ways to Move Salesforce → S3 (Ranked by Use Case)

⭐ 1️⃣ AppFlow — Fully managed, easiest, no code

⭐ 2️⃣ Lambda + Salesforce API — Most flexible
You write Lambda code to call:
Salesforce Bulk API (best for large datasets)
Salesforce REST API
Salesforce SOAP API

⭐ 3️⃣ Salesforce → EventBridge — Real‑time events

⭐ 4️⃣ MuleSoft — Enterprise integration platform

