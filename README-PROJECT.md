aws ssm start-session \
  --target i-03866a693e0b236b9 \
  --region us-east-1
# sh-5.2$

  PGPASSWORD='UseSomethingStrong123!' psql \
  -h dev-hospitality-workgroup.502845302465.us-east-1.redshift-serverless.amazonaws.com \
  -p 5439 \
  -U adminuser \
  -d hospitality
# hospitality=#

SELECT COUNT(*) FROM salesforce_accounts;
#   count 
#  -------
#     4
#  (1 row)

SELECT *
FROM salesforce_accounts;

 account_id |    account_name     |  industry   |   city    | state | annual_revenue 
------------+---------------------+-------------+-----------+-------+----------------
 A001       | Luxury Grand Hotel  | Hospitality | Miami     | FL    |    25000000.00
 A002       | Royal Beach Resort  | Hospitality | Orlando   | FL    |    18000000.00
 A003       | Mountain View Lodge | Hospitality | Denver    | CO    |     9000000.00
 A004       | Ocean Breeze Resort | Hospitality | San Diego | CA    |    32000000.00
(4 rows)




1-  I built a cloud data platform on AWS using Terraform and GitHub Actions. 
2-  I provisioned a VPC with public and private networking, 
    deployed Redshift Serverless for analytics workloads, 
    and created an EC2 jump server for secure administrative access. 
3-  I configured Terraform remote state in S3 with DynamoDB state locking and 
    implemented CI/CD pipelines using GitHub Actions with AWS OIDC authentication to eliminate long-lived credentials. 
4-  For security, I used IAM roles, Security Groups, encrypted resources, and AWS Systems Manager Session Manager instead of SSH access. 
5-  I validated the platform end-to-end by connecting from the EC2 instance to a private Redshift Serverless endpoint, 
    creating database objects, loading data, and  executing SQL queries successfully.

# "What challenges did you face?":

During implementation, I encountered several IAM permission issues with Terraform, including Redshift Serverless, EC2, Security Groups, and IAM role management. 
I followed the principle of least privilege by granting only the required permissions as Terraform reported them. 
I also troubleshot Session Manager connectivity issues, which involved verifying the EC2 IAM role, network routing through the Internet Gateway, installing the Session Manager plugin locally, and ensuring I was using the correct AWS account profile.


# 1. Terraform backend
S3 bucket: hospitality-terraform-state-502845302465
DynamoDB table: hospitality-terraform-locks

# 2. S3 component
Created reusable module
versioning
encryption
public access block
lifecycle rule
abort incomplete multipart uploads

# 3. GitHub Actions pipeline
PR → fmt → validate → Checkov → plan
Push to dev/stage/prod → apply
Manual workflow_dispatch → plan/apply/destroy

# 4. Networking component
Created VPC module
VPC
Public subnets
Private subnets
Internet Gateway
Public route table
Route table associations

# 5. Redshift Serverless component
Redshift subnet group
Redshift Serverless namespace
Redshift Serverless workgroup
Redshift security group
Ingress rule for port 5439 from VPC CIDR

Result:
Namespace: dev-hospitality-namespace
Workgroup: dev-hospitality-workgroup
Status: AVAILABLE
Endpoint: dev-hospitality-workgroup.502845302465.us-east-1.redshift-serverless.amazonaws.com
Port: 5439

# 6. EC2 jump server
EC2 jump server
SSM IAM role
IAM instance profile
AmazonSSMManagedInstanceCore attachment
Encrypted root volume
IMDSv2 required
Detailed monitoring

# 7. SSM Session Manager access
Installed plugin locally and fixed PATH.
Checked AWS profile: 
<bash>
ls "/c/Program Files/Amazon/SessionManagerPlugin/bin"
export PATH="$PATH:/c/Program Files/Amazon/SessionManagerPlugin/bin"

aws configure --profile sam-user-dev

aws sts get-caller-identity --profile sam-user-dev
export AWS_PROFILE=sam-user-dev
aws sts get-caller-identity

terraform -chdir=terraform/components/redshift apply \
  -var="environment=dev" \
  -var="master_password=UseSomethingStrong123!"

<powershell> 
$env:AWS_PROFILE="sam-user-dev"
aws sts get-caller-identity
aws ssm start-session --target i-03866a693e0b236b9 --region us-east-1

============
PGPASSWORD='UseSomethingStrong123!' psql \
  -h dev-hospitality-workgroup.502845302465.us-east-1.redshift-serverless.amazonaws.com \
  -p 5439 \
  -U adminuser \
  -d hospitality

CREATE TABLE salesforce_accounts (
    account_id VARCHAR(20),
    account_name VARCHAR(100),
    industry VARCHAR(50),
    city VARCHAR(50),
    state VARCHAR(10),
    annual_revenue DECIMAL(18,2)
);

COPY salesforce_accounts
FROM 's3://luxury-data-platform-dev-12345/raw/salesforce/accounts/salesforce_accounts.csv'
IAM_ROLE 'arn:aws:iam::502845302465:role/dev-redshift-s3-access-role'
CSV
IGNOREHEADER 1;

SELECT * FROM salesforce_accounts;

aws s3 cp salesforce_opportunities.csv \
s3://luxury-data-platform-dev-12345/raw/salesforce/opportunities/salesforce_opportunities.csv \
--region us-east-1

aws s3 ls s3://luxury-data-platform-dev-12345/raw/salesforce/opportunities/ --region us-east-1

aws ssm start-session --target i-03866a693e0b236b9 --region us-east-1
==============
PGPASSWORD='UseSomethingStrong123!' psql \
  -h dev-hospitality-workgroup.502845302465.us-east-1.redshift-serverless.amazonaws.com \
  -p 5439 \
  -U adminuser \
  -d hospitality

CREATE TABLE salesforce_opportunities (
    opportunity_id VARCHAR(20),
    account_id VARCHAR(20),
    opportunity_name VARCHAR(100),
    stage VARCHAR(50),
    amount DECIMAL(18,2)
);

COPY salesforce_opportunities
FROM 's3://luxury-data-platform-dev-12345/raw/salesforce/opportunities/salesforce_opportunities.csv'
IAM_ROLE 'arn:aws:iam::502845302465:role/dev-redshift-s3-access-role'
CSV
IGNOREHEADER 1;

============
So right now:

Database = hospitality
Schema = public
Tables = hotels, salesforce_accounts, salesforce_opportunities

1-
SELECT current_database();

current_database 
--------------------------
hospitality

2-
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';

      table_name        
--------------------------
 hotels
 salesforce_accounts
 salesforce_opportunities

3-
 SELECT * FROM salesforce_accounts ;
 account_id |    account_name     |  industry   |   city    | state | annual_revenue 
------------+---------------------+-------------+-----------+-------+----------------
 A001       | Luxury Grand Hotel  | Hospitality | Miami     | FL    |    25000000.00
 A002       | Royal Beach Resort  | Hospitality | Orlando   | FL    |    18000000.00
 A003       | Mountain View Lodge | Hospitality | Denver    | CO    |     9000000.00
 A004       | Ocean Breeze Resort | Hospitality | San Diego | CA    |    32000000.00

 4-
 SELECT * FROM salesforce_opportunities ;
 opportunity_id | account_id |     opportunity_name      |    stage    |   amount   
----------------+------------+---------------------------+-------------+------------
 O001           | A001       | Hotel Expansion           | Closed Won  | 5000000.00
 O002           | A002       | Beach Renovation          | Negotiation | 2500000.00
 O003           | A001       | Luxury Suites Upgrade     | Prospecting | 1200000.00
 O004           | A004       | Conference Center Project | Closed Won  | 8000000.00


# Now run your first analytics query.
# Which hotel accounts have opportunities, what stage are they in, and how much revenue is associated with them?
SELECT
    a.account_name,
    o.opportunity_name,
    o.stage,
    o.amount
FROM salesforce_accounts a
JOIN salesforce_opportunities o
    ON a.account_id = o.account_id;

 account_name     |     opportunity_name      |    stage    |   amount   
---------------------+---------------------------+-------------+------------
 Luxury Grand Hotel  | Hotel Expansion           | Closed Won  | 5000000.00
 Royal Beach Resort  | Beach Renovation          | Negotiation | 2500000.00
 Luxury Grand Hotel  | Luxury Suites Upgrade     | Prospecting | 1200000.00
 Ocean Breeze Resort | Conference Center Project | Closed Won  | 8000000.00

# total opportunity revenue per hotel account.
SELECT
    a.account_name,
    SUM(o.amount) AS total_pipeline
FROM salesforce_accounts a
JOIN salesforce_opportunities o
    ON a.account_id = o.account_id
GROUP BY a.account_name
ORDER BY total_pipeline DESC;

 account_name     | total_pipeline 
---------------------+----------------
 Ocean Breeze Resort |     8000000.00
 Luxury Grand Hotel  |     6200000.00
 Royal Beach Resort  |     2500000.00

<Why-SSM>:
No SSH key
No port 22
No inbound rule
IAM-based access
Auditable access
Works with private instances if networking is configured

# 8. Installed psql on EC2
Inside SSM session:
sudo dnf install postgresql15 -y
psql --version

# 9. Connected EC2 to private Redshift
From EC2:
PGPASSWORD='UseSomethingStrong123!' psql \
  -h dev-hospitality-workgroup.502845302465.us-east-1.redshift-serverless.amazonaws.com \
  -p 5439 \
  -U adminuser \
  -d hospitality

# Verified database:
SELECT current_database();

# Created table:
CREATE TABLE hotels (
    hotel_id INT,
    hotel_name VARCHAR(100),
    city VARCHAR(100),
    rooms INT
);

# Inserted data:
INSERT INTO hotels VALUES
(1, 'Luxury Grand Hotel', 'Miami', 250),
(2, 'Royal Beach Resort', 'Orlando', 180);

# SELECT * FROM hotels;
hotel_id |     hotel_name     |  city   | rooms
---------+--------------------+---------+------
1        | Luxury Grand Hotel | Miami   | 250
2        | Royal Beach Resort | Orlando | 180


GitHub Actions
   ↓
OIDC authentication
   ↓
Terraform
   ↓
S3 remote state + DynamoDB locking
   ↓
AWS infrastructure
   ├── S3 data buckets
   ├── VPC
   ├── Public subnets
   ├── Private subnets
   ├── Internet Gateway
   ├── Route tables
   ├── EC2 jump server
   ├── SSM Session Manager
   └── Redshift Serverless

For that job description, the best next architecture is:
Salesforce
   ↓
Export / API extraction
   ↓
S3 raw data bucket
   ↓
Redshift COPY
   ↓
SQL analytics tables

# Next step: create Salesforce-style CSV files
salesforce_accounts.csv
account_id,account_name,industry,city,state,annual_revenue
A001,Luxury Grand Hotel,Hospitality,Miami,FL,25000000
A002,Royal Beach Resort,Hospitality,Orlando,FL,18000000
A003,Mountain View Lodge,Hospitality,Denver,CO,9000000
A004,Ocean Breeze Resort,Hospitality,San Diego,CA,32000000

aws s3 cp salesforce_accounts.csv s3://luxury-data-platform-dev-12345/raw/salesforce/accounts/salesforce_accounts.csv --region us-east-1
aws s3 ls s3://luxury-data-platform-dev-12345/raw/salesforce/accounts/ --region us-east-1


aws s3 cp salesforce_opportunities.csv \
s3://luxury-data-platform-dev-12345/raw/salesforce/opportunities/salesforce_opportunities.csv \
--region us-east-1


# I automated ingestion of Salesforce exports into S3 and Redshift using AWS services and Infrastructure as Code.

# Next single step :  Lambda
terraform -chdir=terraform/components/lambda init
terraform -chdir=terraform/components/lambda plan -var="environment=dev"
terraform -chdir=terraform/components/lambda apply -var="environment=dev"

Lambda IAM role
Lambda basic logging policy attachment
Lambda function


aws lambda invoke \
  --function-name dev-s3-redshift-loader \
  --payload '{"test":"hello"}' \
  --cli-binary-format raw-in-base64-out \
  response.json \
  --region us-east-1

cat response.json

# we want:
salesforce_accounts.csv
        ↓
        S3
        ↓
   S3 Event
        ↓
     Lambda
        ↓
  CloudWatch Logs

# allow S3 to invoke Lambda.

# Before
Create CSV
    ↓
Upload to S3
    ↓
Connect to Redshift
    ↓
Run COPY manually

# After S3 Notification
salesforce_accounts.csv
          ↓
      Upload to S3
          ↓
     S3 Event fires
          ↓
 Lambda runs automatically
          ↓
 Processes the file

 events = ["s3:ObjectCreated:*"]
filter_prefix = "raw/salesforce/"
filter_suffix = ".csv"
Whenever someone uploads: raw/salesforce/
AWS automatically does:

Real-world example

A Salesforce export job runs every night:
12:00 AM
   ↓
salesforce_accounts_20260602.csv
   ↓
S3 bucket
   ↓
Lambda triggered automatically
   ↓
Load into Redshift
   ↓
Morning dashboards updated

This is called an event-driven architecture.

  MSYS_NO_PATHCONV=1 aws logs tail /aws/lambda/dev-s3-redshift-loader \
  --region us-east-1 \
  --since 30m

  The log shows this file upload automatically invoked Lambda:
raw/salesforce/accounts/test-trigger-accounts.csv
=================================================================================
A database is software.
A server is a machine that runs software.

🧠 Database = the brain [postgres] [Mysql] [MariaDB] [SQL-Server] [Oracle]
Stores information.
Thinks.
Answers questions.

5️⃣ Redshift
Redshift is a data warehouse (a special kind of database)
AND AWS manages the servers behind it.
It’s built for analytics, not transactions.

🖥️ Server = the body [RDS] service
Runs the brain.
Provides CPU, memory, storage.

# DynamoDB [IS-Both=database-and-server] 
is fully serverless
You don’t manage anything.


⭐ The simplest explanation of all
• Postgres/MySQL = databases
• RDS = AWS running those databases for you
• DynamoDB = database with no server to manage
• Redshift = analytics database with no server to manage