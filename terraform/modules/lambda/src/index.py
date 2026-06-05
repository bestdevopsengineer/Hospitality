# This is an event-driven ingestion pipeline using S3 → Lambda → Redshift Serverless.
# 1. S3 receives a Salesforce CSV file.
# 2. S3 triggers Lambda automatically.
# 3. Lambda identifies the file type (accounts or opportunities).
# 4. Lambda builds a Redshift COPY command.
# 5. Lambda submits the COPY through the Redshift Data API.
# 6. Lambda polls the statement status.
# 7. If FINISHED, the data is loaded into Redshift.
# 8. Analysts can query the data immediately.

import json
import time
import os
import urllib.parse
import boto3

# Create Redshift Data API client
redshift_data = boto3.client("redshift-data")

WORKGROUP = os.environ["REDSHIFT_WORKGROUP"]
DATABASE = os.environ["REDSHIFT_DATABASE"]
ROLE_ARN = os.environ["REDSHIFT_ROLE_ARN"]


def handler(event, context):
    """
    Lambda entry point.

    Trigger:
        S3 ObjectCreated event

    Purpose:
        Detect uploaded Salesforce CSV files and load them
        into Redshift Serverless using the COPY command.
    """
    # Print the full event for troubleshooting
    print("Received event:")
    print(json.dumps(event))

    # Process all records included in the S3 event
    for record in event.get("Records", []):
        # Extract bucket name and object key from event
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

        # Build full S3 path
        s3_path = f"s3://{bucket}/{key}"

        # Determine target table based on file name/path
        if "accounts" in key:
            table_name = "staging_salesforce_accounts"
        elif "opportunities" in key:
            table_name = "staging_salesforce_opportunities"
        else:
            # Ignore unsupported files
            print(f"Skipping unknown file type: {key}")
            continue
        
        # Build Redshift COPY command
        # sql = f"""
        # COPY {table_name}
        # FROM '{s3_path}'
        # IAM_ROLE '{ROLE_ARN}'
        # CSV
        # IGNOREHEADER 1;
        # """
        if table_name == "staging_salesforce_accounts":
            sql = f"""
            COPY staging_salesforce_accounts
            FROM '{s3_path}'
            IAM_ROLE '{ROLE_ARN}'
            CSV
            IGNOREHEADER 1;

            INSERT INTO salesforce_accounts_errors (
                account_id,
                account_name,
                industry,
                city,
                state,
                annual_revenue,
                error_reason
            )
            SELECT
                account_id,
                account_name,
                industry,
                city,
                state,
                annual_revenue,
                CASE
                    WHEN account_id IS NULL THEN 'Missing account_id'
                    WHEN account_name IS NULL THEN 'Missing account_name'
                    WHEN annual_revenue < 0 THEN 'Negative annual_revenue'
                    ELSE 'Unknown error'
                END
            FROM staging_salesforce_accounts
            WHERE account_id IS NULL
            OR account_name IS NULL
            OR annual_revenue < 0;

            MERGE INTO salesforce_accounts
            USING (
                SELECT *
                FROM staging_salesforce_accounts
                WHERE account_id IS NOT NULL
                AND account_name IS NOT NULL
                AND annual_revenue >= 0
            ) staging_salesforce_accounts
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

            TRUNCATE TABLE staging_salesforce_accounts;
            """
        elif table_name == "staging_salesforce_opportunities":
            sql = f"""
            COPY staging_salesforce_opportunities
            FROM '{s3_path}'
            IAM_ROLE '{ROLE_ARN}'
            CSV
            IGNOREHEADER 1;

            MERGE INTO salesforce_opportunities
            USING staging_salesforce_opportunities
            ON salesforce_opportunities.opportunity_id = staging_salesforce_opportunities.opportunity_id
            WHEN MATCHED THEN UPDATE SET
                account_id = staging_salesforce_opportunities.account_id,
                opportunity_name = staging_salesforce_opportunities.opportunity_name,
                stage = staging_salesforce_opportunities.stage,
                amount = staging_salesforce_opportunities.amount
            WHEN NOT MATCHED THEN INSERT (
                opportunity_id,
                account_id,
                opportunity_name,
                stage,
                amount
            )
            VALUES (
                staging_salesforce_opportunities.opportunity_id,
                staging_salesforce_opportunities.account_id,
                staging_salesforce_opportunities.opportunity_name,
                staging_salesforce_opportunities.stage,
                staging_salesforce_opportunities.amount
            );

            TRUNCATE TABLE staging_salesforce_opportunities;
            """
        else:
            sql = f"""
            COPY {table_name}
            FROM '{s3_path}'
            IAM_ROLE '{ROLE_ARN}'
            CSV
            IGNOREHEADER 1;
            """

        print(f"Executing COPY into {table_name}")
        print(sql)

        # Submit SQL statement to Redshift Serverless
        response = redshift_data.execute_statement(
            WorkgroupName=WORKGROUP,
            Database=DATABASE,
            Sql=sql
        )

        # Store statement id so we can monitor execution
        print(f"Statement ID: {response['Id']}")
        statement_id = response["Id"]

        # Poll Redshift until query completes
        for _ in range(30):
            status = redshift_data.describe_statement(Id=statement_id)
            print(f"Statement status: {status['Status']}")

            # Stop polling once query finishes
            if status["Status"] in ["FINISHED", "FAILED", "ABORTED"]:
                print(json.dumps(status, default=str))
                break

            # Wait before checking again        
            time.sleep(2)

    # Return success response to Lambda caller
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "S3 file submitted to Redshift COPY"})
    }