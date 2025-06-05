# python_scripts_inf
testing python scripts with remote execution in lambda aws



zip test-func.zip test-lambda.py

create trust-policy.json

aws iam create-role \
  --role-name lambda-basic-exec \
  --assume-role-policy-document file://trust-policy.json

aws iam attach-role-policy \
  --role-name lambda-basic-exec \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws lambda create-function   --function-name echo-lambda-fn   --runtime python3.12   --role arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/lambda-basic-exec   --handler lambda_function.lambda_handler   --zip-file fileb://test-func.zip


