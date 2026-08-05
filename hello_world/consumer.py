import json
import os
import boto3

ENDPOINT_URL = os.environ.get("LOCALSTACK_ENDPOINT", "http://localhost:4566")

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url=ENDPOINT_URL,
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

table = dynamodb.Table("DevUsers")

# Official Answer Key for the 5 AWS Certification Questions
ANSWER_KEY = {
    "q1": "SQS",
    "q2": "VisibilityTimeout",
    "q3": "Query",
    "q4": "Throttling",
    "q5": "15min"
}

def handler(event, context):
    print(f"Received {len(event.get('Records', []))} SQS message(s)...")

    for record in event.get("Records", []):
        try:
            message_body = json.loads(record["body"])
            task_id = message_body.get("task_id")
            user_answers = message_body.get("answers", {})

            # Calculate score dynamically
            score = 0
            total = len(ANSWER_KEY)
            for q_id, correct_ans in ANSWER_KEY.items():
                if user_answers.get(q_id) == correct_ans:
                    score += 1

            percentage = round((score / total) * 100, 1)

            item = {
                "id": task_id,
                "role": message_body.get("role", "AWS Dev Candidate"),
                "status": "COMPLETED",
                "score": f"{score}/{total}",
                "percentage": f"{percentage}%"
            }

            table.put_item(Item=item)
            print(f"✅ Successfully processed task {task_id} with score {score}/{total} ({percentage}%)")

        except Exception as e:
            print(f"❌ Failed to process message: {str(e)}")
            raise e