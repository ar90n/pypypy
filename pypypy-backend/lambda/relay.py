import os

import boto3
import botocore.exceptions

TABLE_NAME = "pypypy-websocket-connection"

stage = os.environ["STAGE"]
region = os.environ["AWS_REGION"]
api_id = os.environ["API_ID"]

table = boto3.resource("dynamodb").Table(TABLE_NAME)
api_gateway = boto3.client(
    "apigatewaymanagementapi",
    endpoint_url=f"https://{api_id}.execute-api.{region}.amazonaws.com/{stage}",
)


def get_all_connections(table):
    kwargs = {}
    while True:
        res = table.scan(**kwargs)
        for item in res.get("Items", []):
            yield item["connectionId"]

        exclusive_start_key = res.get("LastEvaluatedKey")
        if exclusive_start_key is None:
            break
        kwargs = {"ExclusiveStartKey": exclusive_start_key}


def handler(event, context):
    data = event["body"]

    for con in get_all_connections(table):
        try:
            api_gateway.post_to_connection(Data=data, ConnectionId=con)
        except botocore.exceptions.ClientError:
            table.delete_item(Key={"connectionId": con})
    return {"statusCode": 200, "body": "OK"}
