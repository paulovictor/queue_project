import json

import pytest
import operator

from client import app
from unittest import mock
from typing import NamedTuple


class Message(NamedTuple):
    body: dict

    def delete(self):
        return True


@pytest.fixture()
def lambda_event():
    return {"body": {}}


@pytest.fixture()
def message_data():
    return Message(json.dumps({
        'function': 'sum',
        'args': [2, 3]
        }))


@mock.patch("client.app.process")
@mock.patch("client.app.receive_message")
def test_handler(mock_receive_message, mock_process, lambda_event, message_data):
    mock_receive_message.return_value = message_data
    mock_process.return_value = (10, None)
    response = app.lambda_handler(lambda_event, '')

    data = json.loads(response["body"])

    assert response["statusCode"] == 200

    assert "function" in data.keys()
    assert "args" in data.keys()
    assert "result" in data.keys()


def test_get_data(message_data):
    response = app.get_data(message_data)
    assert response == ('sum', [2, 3])


@pytest.mark.parametrize('func_name, expected_function', [
    ('sum', operator.add),
    ('subtract', operator.sub),
    ('divide', operator.truediv),
    ('multiply', operator.mul),
])
def test_get_function(func_name, expected_function):
    response = app.get_function(func_name)
    assert response == expected_function


@mock.patch("boto3.resource")
def test_get_queue(mock_boto):
    mock_sqs = mock_boto.return_value
    mock_sqs.get_queue_by_name.return_value = 'newton_queue'
    response = app.get_queue()

    assert response == 'newton_queue'
    mock_boto.assert_called_once_with('sqs')
    mock_sqs.get_queue_by_name.assert_called_once_with(QueueName='newton_sqs.fifo')


@mock.patch("client.app.get_queue")
def test_receive_message(mock_get_queue):
    mock_queue = mock_get_queue.return_value
    mock_queue.receive_messages.return_value = [{'message': 1}]
    response = app.receive_message()

    assert response == {'message': 1}

    mock_get_queue.assert_called_once_with()
    mock_queue.receive_messages.assert_called_once_with(MaxNumberOfMessages=1)


@mock.patch("uuid.uuid4")
@mock.patch("client.app.dynamodb")
def test_process(mock_dynamo, mock_uuid):
    mock_uuid.return_value = 'uuid-1234'
    response = app.process('sum', [1, 2])

    assert response == (3, None)

    mock_dynamo.Table.assert_called_once_with('queue_results')

    mock_dynamo.Table().put_item.assert_called_once_with(Item={
                'ResultID': 'uuid-1234',
                'function': 'sum',
                'args': [1, 2],
                'result': 3
            })
