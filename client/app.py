import json
import boto3
import operator
from functools import reduce
import uuid


dynamodb = boto3.resource('dynamodb')


def lambda_handler(event, context):
    result = None
    message = receive_message()
    if message:
        function, args_list = get_data(message)
        result, error_message = process(function, args_list)

        message.delete()
    else:
        error_message = 'empty queue'

    if error_message:
        response = {
            'status_code': 500,
            'error': str(error_message)
        }
    else:
        response = {
            'status_code': 200,
            'body': json.dumps({
                'function': function,
                'args': args_list,
                'result': result,
            })}

    return response


def process(function, args_list):
    try:
        _operator = get_function(function)
        result = reduce(_operator, args_list)
    except Exception as e:
        return None, e

    table = dynamodb.Table('queue_results')
    table.put_item(
            Item={
                'ResultID': str(uuid.uuid4()),
                'function': function,
                'args': args_list,
                'result': result
            }
        )
    return result, None


def receive_message():
    queue = get_queue()
    messages = queue.receive_messages(MaxNumberOfMessages=1)
    if messages:
        return messages[0]
    return None


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


def get_table():
    table = dynamodb.Table('employee')
    return table
