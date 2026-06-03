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

