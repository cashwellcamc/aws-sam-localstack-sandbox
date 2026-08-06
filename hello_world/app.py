import json
import uuid
import os
import boto3

ENDPOINT_URL = os.environ.get("LOCALSTACK_ENDPOINT", "http://host.docker.internal:4566")

dynamodb = boto3.resource("dynamodb", endpoint_url=ENDPOINT_URL, region_name="us-east-1", aws_access_key_id="test", aws_secret_access_key="test")
dev_users_table = dynamodb.Table("DevUsers")
quiz_questions_table = dynamodb.Table("QuizQuestions")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    "Content-Type": "application/json"
}

def lambda_handler(event, context):
    http_method = event.get("httpMethod", "POST")
    path = event.get("path", "")

    if http_method == "OPTIONS":
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps({"status": "ok"})}

    # GET /questions: Fetch question bank from DynamoDB
    if http_method == "GET" and "/questions" in path:
        try:
            res = quiz_questions_table.scan()
            items = res.get("Items", [])
            return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps(items)}
        except Exception as e:
            return {"statusCode": 500, "headers": CORS_HEADERS, "body": json.dumps({"error": str(e)})}

    # GET /hello?task_id=... : Poll task status
    if http_method == "GET":
        query_params = event.get("queryStringParameters") or {}
        task_id = query_params.get("task_id")

        if not task_id:
            return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"error": "Missing task_id"})}

        res = dev_users_table.get_item(Key={"id": task_id})
        if "Item" in res:
            return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps(res["Item"])}
        
        return {"statusCode": 404, "headers": CORS_HEADERS, "body": json.dumps({"status": "PENDING"})}

    # POST /hello: Submit & Grade Quiz Directly
    try:
        body = json.loads(event.get("body", "{}"))
        user_answers = body.get("answers", {})
        task_id = str(uuid.uuid4())

        # Pull official question bank and grading keys directly from DynamoDB
        questions_res = quiz_questions_table.scan()
        questions = {q['q_id']: q for q in questions_res.get("Items", [])}

        score = 0
        total = len(questions) or 1
        breakdown = []

        for q_id, q_data in questions.items():
            submitted = str(user_answers.get(q_id, "")).strip()
            expected = str(q_data.get("answer", "")).strip()
            
            is_correct = (submitted.lower() == expected.lower())
            if is_correct:
                score += 1

            breakdown.append({
                "question": q_data.get("question"),
                "submitted": submitted,
                "expected": expected,
                "correct": is_correct,
                "hint": q_data.get("hint", "")
            })

        pct = f"{int((score / total) * 100)}%"

        # Write final graded record directly into DevUsers table
        dev_users_table.put_item(
            Item={
                "id": task_id,
                "status": "COMPLETED",
                "score": f"{score}/{total}",
                "percentage": pct,
                "breakdown": json.dumps(breakdown)
            }
        )

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"message": "Quiz graded successfully", "task_id": task_id})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)})
        }