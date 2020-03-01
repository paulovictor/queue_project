import json
import boto3
import operator
from functools import reduce


def lambda_handler(event, context):
    message = receive_message()
    function, args = get_data(message)
    _operator = get_function(function)
    result = reduce(_operator, args)

    message.delete()
    return {
        "statusCode": 200,
        "body": json.dumps({
            "function": function,
            "args": args,
            "result": result,
        }),
    }


def receive_message():
    queue = get_queue()
    return queue.receive_messages(MaxNumberOfMessages=1)[0]


def get_queue():
    sqs = boto3.resource('sqs')
    return sqs.get_queue_by_name(QueueName='newton_sqs.fifo')


def get_data(message):
    body = json.loads(message.body)
    function = body.get('function')
    args = body.get('args')
    return function, args


def get_function(function_name):
    _functions = {
        'sum': operator.add,
        'subtract': operator.sub,
        'divide': operator.truediv,
        'multiply': operator.mul,
    }
    return _functions[function_name]
