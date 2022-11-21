import asyncio
from unittest.mock import patch

from source.url_checker import (
    NOT_AVAILABLE_METHODS, NOT_URL, parse_args, validate
)


def test_parse_args():
    args = parse_args(['sos', 'http://google.com', 'alex', 'sos'])
    assert {'sos', 'http://google.com', 'alex'} == args


def test_validate_not_url():
    result = asyncio.run(validate({'a'}))
    assert result == {'a': NOT_URL % 'a'}


@patch('source.url_checker.get_data')
def test_validate_url(get_data_mock):
    url = 'https://wwww.google.com'
    get_data_mock.return_value = url, {'GET': 200, 'HEAD': 200}
    result = asyncio.run(validate({url}))
    assert result == dict([(url, {'GET': 200, 'HEAD': 200})])


@patch('source.url_checker.get_data')
def test_validate_url_without_method(get_data_mock):
    url = 'https://wwww.google.com'
    get_data_mock.return_value = url, NOT_AVAILABLE_METHODS % url
    result = asyncio.run(validate({url}))
    assert result == dict([(url, NOT_AVAILABLE_METHODS % url)])
