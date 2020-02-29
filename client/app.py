import json
import boto3
import uuid


def lambda_handler(event, context):
    body = event["body"]
    response = get_queue(body)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message_id": response,
            "event": body,
        }),
    }


def get_queue():
    sqs = boto3.resource('sqs')
    return sqs.get_queue_by_name(QueueName='newton_sqs.fifo')


# def send_message(body):
#     queue = get_queue()
#     return queue.send_message(MessageBody=body, MessageGroupId=str(uuid.uuid4()))
