import json

# import requests

def lambda_handler(event, context):
    # Extract query parameters (e.g. ?name=Cameron)
    query_params = event.get("queryStringParameters") or {}
    name = query_params.get("name", "Developer")
    
    # Parse incoming JSON body if it's a POST request
    body_data = {}
    if event.get("body"):
        try:
            body_data = json.loads(event["body"])
        except json.JSONDecodeError:
            pass

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message": f"Welcome aboard, {name}!",
            "received_body": body_data,
            "http_method": event.get("httpMethod")
        }),
    }

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world from RVA. LFGO NERDS !!!",
            # "location": ip.text.replace("\n", "")
        }),
    }
