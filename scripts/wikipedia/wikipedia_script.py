import json
import requests
import boto3
import os
from botocore.client import Config as BotoConfig
from botocore.exceptions import ClientError


def get_s3_client():
    """
    Return an S3 client configured to the specified region with path-style addressing.
    """
    return boto3.client(
        "s3",
        region_name=os.environ.get("BUCKET_REGION", "eu-north-1"),
        config=BotoConfig(
            signature_version="s3v4",
            s3={"addressing_style": "path"}
        )
    )


def get_s3_content(bucket: str, key: str) -> str:
    """
    Retrieve the current content of an S3 object, or return empty string if not found.
    """
    s3 = get_s3_client()
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        return response['Body'].read().decode('utf-8')
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return ""
        raise


def put_s3_content(bucket: str, key: str, content: str):
    """
    Upload content to an S3 object, overwriting any existing data.
    """
    s3 = get_s3_client()
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=content.encode('utf-8')
    )


def lambda_handler(event, context):
    """
    AWS Lambda handler that supports two modes:

    1. Append mode (POST):
       - Expects JSON body with {'title': '...'}
       - Fetches the Wikipedia summary
       - Appends it to the S3 object
       - Returns the full file contents with Content-Disposition attachment headers

    2. Download mode (GET with ?action=download):
       - Reads full S3 object and returns it with attachment headers

    Environment variables:
      - BUCKET_NAME: name of the S3 bucket
      - BUCKET_REGION: (optional) region for S3 operations
      - FILE_KEY: (optional) key for the object (default 'summaries.txt')
    """
    bucket = os.environ['BUCKET_NAME']
    key = os.environ.get('FILE_KEY', 'summaries.txt')

    # Append & download on POST
    if event.get('body'):
        try:
            body = json.loads(event['body'])
            title = body.get('title', '').strip()
            if not title:
                return {'statusCode': 400, 'body': json.dumps({'error': 'Missing title'})}

            # Fetch Wikipedia summary
            encoded = title.replace(' ', '_')
            url = f'https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}'
            res = requests.get(url, timeout=10)
            data = res.json()
            summary = data.get('extract', 'No summary found.')

            # Append to existing S3 file
            current = get_s3_content(bucket, key)
            separator = '\n' + '*'*40 + '\n'
            updated = f"{current}{separator}{title}\n\n{summary}\n"
            put_s3_content(bucket, key, updated)

            # Read back full file
            full = get_s3_content(bucket, key)
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/plain',
                    'Content-Disposition': f'attachment; filename={key}'
                },
                'body': full
            }
        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}

    # Download mode on GET
    params = event.get('queryStringParameters') or {}
    if params.get('action') == 'download':
        try:
            content = get_s3_content(bucket, key)
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/plain',
                    'Content-Disposition': f'attachment; filename={key}'
                },
                'body': content
            }
        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}

    # Bad request for other methods
    return {'statusCode': 400, 'body': json.dumps({'error': 'Bad request'})}

