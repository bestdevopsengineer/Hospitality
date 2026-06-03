import json
import time
import os
import urllib.parse
import boto3

redshift_data = boto3.client("redshift-data")

WORKGROUP = os.environ["REDSHIFT_WORKGROUP"]
DATABASE = os.environ["REDSHIFT_DATABASE"]
ROLE_ARN = os.environ["REDSHIFT_ROLE_ARN"]


def handler(event, context):
    print("Received event:")
    print(json.dumps(event))

    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

        s3_path = f"s3://{bucket}/{key}"

        if "accounts" in key:
            table_name = "salesforce_accounts"
        elif "opportunities" in key:
            table_name = "salesforce_opportunities"
        else:
            print(f"Skipping unknown file type: {key}")
            continue

        sql = f"""
        COPY {table_name}
        FROM '{s3_path}'
        IAM_ROLE '{ROLE_ARN}'
        CSV
        IGNOREHEADER 1;
        """

        print(f"Executing COPY into {table_name}")
        print(sql)

        response = redshift_data.execute_statement(
            WorkgroupName=WORKGROUP,
            Database=DATABASE,
            Sql=sql
        )

        print(f"Statement ID: {response['Id']}")

        for _ in range(10):
            status = redshift_data.describe_statement(Id=statement_id)
            print(f"Statement status: {status['Status']}")

            if status["Status"] in ["FINISHED", "FAILED", "ABORTED"]:
                print(json.dumps(status, default=str))
                break

            time.sleep(2)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "S3 file submitted to Redshift COPY"})
    }