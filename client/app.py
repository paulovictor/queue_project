import json
import boto3
import operator
from functools import reduce


def lambda_handler(event, context):
    messages = receive_message()
    body = json.loads(messages[0].body)
    function = body.get('function')
    args = body.get('args')

    _operator = get_function(function)
    result = reduce(_operator, args)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "function": function,
            "args": args,
            "result": result,
        }),
    }


def get_function(function_name):
    _functions = {
        'sum': operator.add,
        'subtract': operator.sub,
        'divide': operator.truediv,
        'multiply': operator.mul,
    }
    return _functions[function_name]


def get_queue():
    sqs = boto3.resource('sqs')
    return sqs.get_queue_by_name(QueueName='newton_sqs.fifo')


def receive_message():
    queue = get_queue()
    return queue.receive_messages(
        MaxNumberOfMessages=1
        )
