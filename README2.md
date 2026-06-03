Salesforce
 ↓
S3
 ↓
Lambda
 ↓
COPY
 ↓
FINISHED ? ── Yes ──► Data available in Redshift

             No
             ↓
        CloudWatch
             ↓
          SNS
             ↓
      Email/Slack
             ↓
      Move file to error/


# 1. Infrastructure Foundation (Terraform)
You provisioned on AWS:
VPC
├── Public Subnet
├── Private Subnet
├── Internet Gateway
├── Route Tables
└── Security Groups

EC2 Jump Server
└── Access via AWS Systems Manager (SSM)

Redshift Serverless
├── Namespace
└── Workgroup

S3
├── Terraform State Bucket
└── Data Lake Bucket

DynamoDB
└── Terraform State Locking

You used:
Terraform
GitHub Actions
AWS OIDC
Remote State

# 2. Salesforce Data Simulation
Because we don't have a real Salesforce org, we simulated Salesforce exports.
Created:
salesforce_accounts.csv
salesforce_opportunities.csv

Uploaded them to:
s3://luxury-data-platform-dev-12345/raw/salesforce/accounts/
s3://luxury-data-platform-dev-12345/raw/salesforce/opportunities/

# 3. Manual Data Loading
Initially we loaded manually.
Created Redshift tables:
salesforce_accounts
salesforce_opportunities

Ran:

COPY salesforce_accounts
FROM 's3://...'
IAM_ROLE '...'
CSV
IGNOREHEADER 1;

COPY salesforce_opportunities
FROM 's3://...'
IAM_ROLE '...'
CSV
IGNOREHEADER 1;

Verified:
SELECT * FROM salesforce_accounts;
SELECT * FROM salesforce_opportunities;

# 4. Analytics Layer
Ran business queries.
Example:
SELECT
    a.account_name,
    o.opportunity_name,
    o.stage,
    o.amount
FROM salesforce_accounts a
JOIN salesforce_opportunities o
ON a.account_id = o.account_id;

SELECT
    a.account_name,
    SUM(o.amount)
FROM salesforce_accounts a
JOIN salesforce_opportunities o
ON a.account_id = o.account_id
GROUP BY a.account_name;

This demonstrated:

Salesforce CRM Data
        ↓
Redshift
        ↓
Business Analytics

# 5. Event Driven Architecture
Then we automated everything.
Created:
Lambda

Configured:

S3 Event Notification

Trigger:

raw/salesforce/
*.csv

Meaning:

New CSV lands in S3
       ↓
Lambda runs automatically

# 6. Lambda Logic
Lambda now:
Receives S3 Event
      ↓
Determines file type
      ↓
Accounts?
      ↓
COPY salesforce_accounts

OR

Opportunities?
      ↓
COPY salesforce_opportunities

Using:
boto3
Redshift Data API

# 7. IAM Permissions

Added:
Redshift Data API permissions

redshift-data:ExecuteStatement
redshift-data:DescribeStatement
redshift-serverless:GetCredentials

Also granted Redshift table permissions:
GRANT INSERT, SELECT
ON salesforce_accounts
TO "IAMR:dev-s3-redshift-loader-role";

# 8. Final Validation

Uploaded:
permission-test-accounts.csv
Observed:
S3 Event
 ↓
Lambda
 ↓
COPY
 ↓
Statement status: FINISHED

Then verified:
SELECT COUNT(*) FROM salesforce_accounts;

Result:
Before = 4
After  = 8

Meaning:
New file landed in S3
      ↓
Lambda automatically loaded Redshift
      ↓
Rows increased

# Current Architecture
Salesforce
    ↓
CSV Export
    ↓
S3 (raw/salesforce)
    ↓
S3 Event Notification
    ↓
Lambda
    ↓
Redshift Data API
    ↓
COPY Command
    ↓
Redshift Serverless
    ↓
Analytics Queries

Salesforce
→ S3 Data Lake
→ Event Driven Lambda
→ Redshift Serverless
→ SQL Analytics
→ Terraform
→ GitHub Actions
→ OIDC Authentication
→ SSM Access
→ Remote State + DynamoDB Locking

The next logical enhancement would be to add a staging (raw → staging → curated) layer with UPSERT/MERGE logic, 
because that's what production data engineering teams usually do instead of loading directly into final tables. 

Option 1:
S3 Event Notification → Lambda

Option 2:
S3 → EventBridge → Lambda

=========
Why we used S3 Event Notification first
Because it is simpler:

S3 file uploaded
   ↓
Lambda runs

Good for learning and quick demos.

============
Why EventBridge is better for production

EventBridge gives more control:

S3
 ↓
EventBridge Rule
 ↓
Lambda

Benefits:
Better routing
Better filtering
Easier to send event to multiple targets
Better for enterprise event-driven architecture
Can connect future workflows like Step Functions

# For the first version, I used S3 Event Notification to trigger Lambda directly when Salesforce CSV files land in S3. 
# In production, I would likely use EventBridge between S3 and Lambda for better event routing, filtering, retry handling, 
# and future extensibility.

# Right now:

S3 raw file
   ↓
Lambda COPY
   ↓
salesforce_accounts final table

# Better production design:

S3 raw file
   ↓
Lambda COPY
   ↓
staging table
   ↓
MERGE / UPSERT
   ↓
curated final table

# Because raw files can have:
duplicate records
updated records
bad data
missing values
schema changes

# So instead of loading directly into the final table, we load into:
staging_salesforce_accounts

# Then run:
MERGE INTO salesforce_accounts
USING staging_salesforce_accounts
ON salesforce_accounts.account_id = staging_salesforce_accounts.account_id

# Meaning:
If account_id already exists → UPDATE it
If account_id does not exist → INSERT it

# This is called:
UPSERT = UPDATE + INSERT

Interview version:

In production, I would not load Salesforce files directly into the final reporting table. 
I would first load them into a staging table, validate and clean the data, 
then use MERGE/UPSERT logic to update existing records and insert new records 
into curated Redshift tables. This avoids duplicates and supports incremental Salesforce loads.