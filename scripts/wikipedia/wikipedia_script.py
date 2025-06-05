import requests
import json

def get_wikipedia_summary(title):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data["extract"]
        else:
            return f"Error: Wikipedia returned status {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Network error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        title = body.get("title")

        if not title:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'title' in request body"})
            }

        title = title.strip().replace(" ", "_")
        summary = get_wikipedia_summary(title)

        return {
            "statusCode": 200,
            "body": json.dumps({"title": title.replace("_", " "), "summary": summary})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

