import json
import os
import uuid
import boto3

ENDPOINT_URL = os.environ.get("LOCALSTACK_ENDPOINT", "http://host.docker.internal:4566")

sqs = boto3.client(
    "sqs",
    endpoint_url=ENDPOINT_URL,
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url=ENDPOINT_URL,
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

table = dynamodb.Table("DevUsers")
QUEUE_URL = "http://host.docker.internal:4566/000000000000/DevQueue"

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    "Content-Type": "application/json"
}

def lambda_handler(event, context):
    http_method = event.get("httpMethod", "GET")

    if http_method == "OPTIONS":
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps({"message": "OK"})}

    # GET Request: Check Quiz Results by Task ID
    if http_method == "GET":
        query_params = event.get("queryStringParameters") or {}
        task_id = query_params.get("task_id")

        if not task_id:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Missing task_id query parameter"})
            }

        response = table.get_item(Key={"id": task_id})
        item = response.get("Item")

        if not item:
            return {
                "statusCode": 404,
                "headers": CORS_HEADERS,
                "body": json.dumps({"status": "PROCESSING", "message": "Quiz still in queue..."})
            }

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps(item)
        }

    # POST Request: Queue Submission to SQS
    if http_method == "POST":
        body_data = {}
        if event.get("body"):
            try:
                body_data = json.loads(event["body"])
            except json.JSONDecodeError:
                return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"error": "Invalid JSON"})}

        message_payload = {
            "task_id": str(uuid.uuid4()),
            "role": body_data.get("role", "Quiz Taker"),
            "answers": body_data.get("answers", {}),
            "status": "QUEUED"
        }

        try:
            response = sqs.send_message(
                QueueUrl=QUEUE_URL,
                MessageBody=json.dumps(message_payload)
            )

            return {
                "statusCode": 202,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "message": "Quiz submission queued!",
                    "task_id": message_payload["task_id"],
                    "message_id": response.get("MessageId")
                })
            }
        except Exception as e:
            return {"statusCode": 500, "headers": CORS_HEADERS, "body": json.dumps({"error": str(e)})}

    return {"statusCode": 405, "headers": CORS_HEADERS, "body": json.dumps({"error": "Method Not Allowed"})}