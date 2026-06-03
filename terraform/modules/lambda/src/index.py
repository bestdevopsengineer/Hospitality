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
            table_name = "salesforce_accounts"
        elif "opportunities" in key:
            table_name = "salesforce_opportunities"
        else:
            # Ignore unsupported files
            print(f"Skipping unknown file type: {key}")
            continue
        
        # Build Redshift COPY command
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
        for _ in range(10):
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