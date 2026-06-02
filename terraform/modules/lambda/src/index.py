import json

def handler(event, context):
    print("Received event:")
    print(json.dumps(event))

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "S3 event received successfully"
        })
    }