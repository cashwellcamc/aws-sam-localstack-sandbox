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

# Master Answer Key with explanations for certification study
ANSWER_KEY = {
    "q1": {"answer": "SQS", "hint": "AWS SQS is fully managed message queuing."},
    "q2": {"answer": "VisibilityTimeout", "hint": "Messages enter a Visibility Timeout while being processed."},
    "q3": {"answer": "Query", "hint": "Query retrieves items with a matching Partition Key efficiently."},
    "q4": {"answer": "Throttling", "hint": "API Gateway uses token bucket throttling to control request rates."},
    "q5": {"answer": "15min", "hint": "The maximum execution time limit for AWS Lambda is 15 minutes."},
    "q6": {"answer": "dynamodb:PutItem", "hint": "IAM action to create/overwrite items is 'dynamodb:PutItem'."},
    "q7": {"answer": "SQS", "hint": "SAM Event Type for SQS integration is simply 'SQS'."},
    "q8": {"answer": "receive_message", "hint": "Boto3 SQS client method name is 'receive_message'."}
}

def handler(event, context):
    print(f"Received {len(event.get('Records', []))} SQS message(s)...")

    for record in event.get("Records", []):
        try:
            message_body = json.loads(record["body"])
            task_id = message_body.get("task_id")
            user_answers = message_body.get("answers", {})

            score = 0
            total = len(ANSWER_KEY)
            breakdown = {}

            for q_id, data in ANSWER_KEY.items():
                user_val = str(user_answers.get(q_id, "")).strip()
                correct_val = data["answer"]
                
                is_correct = (user_val.lower() == correct_val.lower())
                if is_correct:
                    score += 1

                breakdown[q_id] = {
                    "correct": is_correct,
                    "submitted": user_val,
                    "expected": correct_val,
                    "hint": data["hint"] if not is_correct else "Correct!"
                }

            percentage = round((score / total) * 100, 1)

            item = {
                "id": task_id,
                "role": message_body.get("role", "AWS Dev Candidate"),
                "status": "COMPLETED",
                "score": f"{score}/{total}",
                "percentage": f"{percentage}%",
                "breakdown": json.dumps(breakdown)
            }

            table.put_item(Item=item)
            print(f"✅ Successfully processed task {task_id} with detailed breakdown!")

        except Exception as e:
            print(f"❌ Failed to process message: {str(e)}")
            raise e