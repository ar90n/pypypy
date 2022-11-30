import boto3

TABLE_NAME = "pypypy-websocket-connection"


def handler(event, context):
    table = boto3.resource("dynamodb").Table(TABLE_NAME)
    table.delete_item(Key={"connectionId": event["requestContext"]["connectionId"]})

    return {"statusCode": 200, "body": "OK"}
