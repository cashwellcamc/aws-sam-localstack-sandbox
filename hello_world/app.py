import json
import os
import uuid
import boto3

def get_dynamodb_resource():
    # When running under 'sam local', SAM sets environment variables
    # We target host.docker.internal to reach LocalStack running on your Mac host
    endpoint_url = os.environ.get("DYNAMODB_ENDPOINT", "http://host.docker.internal:4566")
    
    return boto3.resource(
        "dynamodb",
        endpoint_url=endpoint_url,
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test"
    )

def lambda_handler(event, context):
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table("DevUsers")
        http_method = event.get("httpMethod", "GET")

        # Handle POST Request: Write Item to DynamoDB
        if http_method == "POST":
            body_data = {}
            if event.get("body"):
                try:
                    body_data = json.loads(event["body"])
                except json.JSONDecodeError:
                    return {"statusCode": 400, "body": json.dumps({"error": "Invalid JSON"})}

            user_id = str(uuid.uuid4())
            item = {
                "id": user_id,
                "role": body_data.get("role", "Developer"),
                "status": body_data.get("status", "active")
            }

            table.put_item(Item=item)

            return {
                "statusCode": 201,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "message": "User saved to DynamoDB!",
                    "saved_item": item
                })
            }

        # Handle GET Request: Fetch All Items
        elif http_method == "GET":
            response = table.scan()
            items = response.get("Items", [])

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "count": len(items),
                    "users": items
                })
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

    return {
        "statusCode": 405,
        "body": json.dumps({"error": "Method Not Allowed"})
    }