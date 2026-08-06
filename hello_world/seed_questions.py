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

# 1. Create QuizQuestions Table
try:
    table = dynamodb.create_table(
        TableName="QuizQuestions",
        KeySchema=[{"AttributeName": "q_id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "q_id", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
    )
    table.wait_until_exists()
    print("✅ Created 'QuizQuestions' table.")
except Exception:
    table = dynamodb.Table("QuizQuestions")
    print("ℹ️ Using existing 'QuizQuestions' table.")

# 2. Comprehensive DVA-C02 Question Bank (15 Questions)
QUESTIONS = [
    # Multiple Choice
    {"q_id": "q1", "type": "mc", "question": "Which AWS service provides fully managed asynchronous message queuing to decouple microservices?", "options": ["SQS", "SNS", "EventBridge"], "answer": "SQS", "hint": "SQS provides managed queueing for decoupling application components."},
    {"q_id": "q2", "type": "mc", "question": "What happens to a message in SQS when a consumer pulls it off the queue for processing?", "options": ["Delete", "VisibilityTimeout", "Archive"], "answer": "VisibilityTimeout", "hint": "Messages enter a Visibility Timeout to prevent other consumers from processing them simultaneously."},
    {"q_id": "q3", "type": "mc", "question": "Which DynamoDB operation returns multiple items matching a primary key attribute efficiently?", "options": ["GetItem", "Query", "Scan"], "answer": "Query", "hint": "Query searches using primary key attributes without inspecting the entire table."},
    {"q_id": "q4", "type": "mc", "question": "How does AWS API Gateway handle high incoming traffic spikes safely?", "options": ["Throttling", "ManualScale", "Drop"], "answer": "Throttling", "hint": "API Gateway uses token bucket algorithm throttling limits."},
    {"q_id": "q5", "type": "mc", "question": "What is the maximum execution timeout limit for an AWS Lambda function?", "options": ["5min", "15min", "60min"], "answer": "15min", "hint": "AWS Lambda max execution time is 900 seconds (15 minutes)."},
    {"q_id": "q6", "type": "mc", "question": "How do you prevent a Lambda function from retrying all messages in an SQS batch when only one fails?", "options": ["ReportBatchItemFailures", "DisableRetry", "SetTimeout0"], "answer": "ReportBatchItemFailures", "hint": "Returning item identifiers in batchItemFailures keeps successful messages deleted."},
    {"q_id": "q7", "type": "mc", "question": "Which DynamoDB expression parameter prevents overwriting an item if a primary key already exists?", "options": ["ConditionExpression", "KeyConditionExpression", "FilterExpression"], "answer": "ConditionExpression", "hint": "Use attribute_not_exists(pk) inside ConditionExpression for optimistic locking."},
    {"q_id": "q8", "type": "mc", "question": "What type of DynamoDB index can be created ANY time after table creation with a different Partition Key?", "options": ["LSI", "GSI", "PSI"], "answer": "GSI", "hint": "Global Secondary Indexes (GSI) can be created or deleted post table creation."},
    {"q_id": "q9", "type": "mc", "question": "Which CloudWatch tool lets you trace user requests end-to-end through serverless services?", "options": ["AWS X-Ray", "CloudTrail", "EventBridge"], "answer": "AWS X-Ray", "hint": "X-Ray traces microservice calls and visualizes service graphs."},
    {"q_id": "q10", "type": "mc", "question": "In SAM templates, which section allows you to define global configuration settings like Runtime and Timeout across all functions?", "options": ["Globals", "Parameters", "Mappings"], "answer": "Globals", "hint": "Globals section defines shared default properties for functions and APIs."},
    
    # Code / Template Remediation
    {"q_id": "q11", "type": "code", "question": "Fix IAM Policy: Provide the exact action string to grant write access for putting items into DynamoDB.", "code": '{\n  "Version": "2012-10-17",\n  "Statement": [{\n    "Effect": "Allow",\n    "Action": ["dynamodb:FetchItem"],\n    "Resource": "arn:aws:dynamodb:us-east-1:000000000000:table/DevUsers"\n  }]\n}', "answer": "dynamodb:PutItem", "hint": "IAM action to put/overwrite items is 'dynamodb:PutItem'."},
    {"q_id": "q12", "type": "code", "question": "Fix SAM Template: Supply the correct Event Type string so SQS triggers the Lambda function.", "code": 'Events:\n  MySQSEvent:\n    Type: SQSQueue\n    Properties:\n      Queue: !GetAtt DevQueue.Arn\n      BatchSize: 10', "answer": "SQS", "hint": "SAM Event Type for SQS integration is 'SQS'."},
    {"q_id": "q13", "type": "code", "question": "Fix Python Boto3 SDK: Replace pop_messages with the correct Boto3 SQS client method name.", "code": 'response = sqs.pop_messages(\n    QueueUrl=queue_url,\n    MaxNumberOfMessages=5\n)', "answer": "receive_message", "hint": "Boto3 SQS client method name is 'receive_message'."},
    {"q_id": "q14", "type": "code", "question": "Fix CloudFormation: Provide the intrinsic function string to reference the ARN attribute of a DynamoDB table named MyTable.", "code": 'TableArn: !Ref MyTable.Arn', "answer": "!GetAtt MyTable.Arn", "hint": "Use !GetAtt logical_id.Arn to retrieve resource ARNs in CloudFormation."},
    {"q_id": "q15", "type": "code", "question": "Fix AWS X-Ray Python SDK: Name the method used to start a custom subsegment in code.", "code": 'xray_recorder.begin_segment("my_subsegment")', "answer": "begin_subsegment", "hint": "Custom tracing logic inside existing segments uses 'begin_subsegment'."}
]

with table.batch_writer() as batch:
    for item in QUESTIONS:
        batch.put_item(Item=item)

print(f"✅ Successfully seeded {len(QUESTIONS)} DVA-C02 exam questions into LocalStack DynamoDB!")