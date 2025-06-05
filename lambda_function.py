def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "body": f"Hello from Lambda! You sent: {event}"
    }
