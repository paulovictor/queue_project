import json

import pytest

from server import app
from unittest import mock


@pytest.fixture()
def lambda_event():
    return {
        "body": {},
    }


@mock.patch("server.app.send_message")
def test_handler(mock_send_message, lambda_event):
    mock_send_message.return_value = {
        "MessageId": "123"
    }
    response = app.lambda_handler(lambda_event, '')

    data = json.loads(response["body"])

    assert response["statusCode"] == 200

    assert "message_id" in data.keys()
    assert data["message_id"] == "123"


@mock.patch("boto3.resource")
def test_get_queue(mock_boto):
    mock_sqs = mock_boto.return_value
    mock_sqs.get_queue_by_name.return_value = 'newton_queue'
    response = app.get_queue()

    assert response == 'newton_queue'
    mock_boto.assert_called_once_with('sqs')
    mock_sqs.get_queue_by_name.assert_called_once_with(QueueName='newton_sqs.fifo')


@mock.patch("uuid.uuid4")
@mock.patch("server.app.get_queue")
def test_send_message(mock_get_queue, mock_uuid):
    mock_uuid.return_value = 'uuid-1234'
    mock_queue = mock_get_queue.return_value
    mock_queue.send_message.return_value = {'message': 1}
    response = app.send_message('newton message')

    assert response == {'message': 1}
    mock_get_queue.assert_called_once_with()
    mock_queue.send_message.assert_called_once_with(
        MessageBody='newton message',
        MessageGroupId='uuid-1234'
        )
