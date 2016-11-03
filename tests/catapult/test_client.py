import unittest
import six
import requests

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.catapult import Client, CatapultException

class ClientTests(unittest.TestCase):
    def test_init_with_right_auth_data(self):
        """
        Client() should return client instance with right auth data
        """
        client = Client('userId', 'apiToken', 'apiSecret')
        self.assertEqual('userId', client.user_id)
        self.assertTupleEqual(('apiToken', 'apiSecret'), client.auth)
        self.assertEqual('https://api.catapult.inetwork.com', client.api_endpoint)
        self.assertEqual('v1', client.api_version)

    def test_init_with_right_auth_data_and_another_endpoint_and_version(self):
        """
        Client() should return client instance with right auth data (different endpoint and version)
        """
        client = Client('userId', 'apiToken', 'apiSecret', api_endpoint = 'url', api_version = 'v2')
        self.assertEqual('userId', client.user_id)
        self.assertTupleEqual(('apiToken', 'apiSecret'), client.auth)
        self.assertEqual('url', client.api_endpoint)
        self.assertEqual('v2', client.api_version)

    @unittest.expectedFailure
    def test_init_with_missing_auth_data(self):
        """
        Client() should raise error on missing auth data
        """
        Client('userId')

    def test_request_with_absolute_url(self):
        """
        _request() should make authorized request to absolute url
        """
        estimated_response = requests.Response()
        estimated_response.status_code = requests.codes['ok']
        with patch('requests.request', return_value = estimated_response) as p:
            client = Client('userId', 'apiToken', 'apiSecret')
            response = client._request('get', 'http://localhost')
            p.assert_called_with('get', 'http://localhost', auth=('apiToken', 'apiSecret'))

    def test_request_with_relative_url(self):
        """
        _request() should make authorized request to relative url
        """
        estimated_response = requests.Response()
        estimated_response.status_code = requests.codes['ok']
        with patch('requests.request', return_value = estimated_response) as p:
            client = Client('userId', 'apiToken', 'apiSecret')
            response = client._request('get', '/path')
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/path', auth=('apiToken', 'apiSecret'))

    def test_check_response_with_json_error(self):
        """
        _check_response() should extract error data from json
        """
        response = requests.Response()
        response.status_code = 400
        response.headers['content-type'] = 'application/json'
        response._content = '{"message": "This is error", "code": "invalid-request"}'
        client = Client('userId', 'apiToken', 'apiSecret')
        with self.assertRaises(CatapultException) as r:
            client._check_response(response)
        err = r.exception
        self.assertEqual('invalid-request', err.code)
        self.assertEqual('This is error', err.message)
        self.assertEqual(400, err.status_code)
        self.assertEqual('Error invalid-request: This is error', str(err))

    def test_check_response_with_json_error_without_code(self):
        """
        _check_response() should extract error data from json (without code)
        """
        response = requests.Response()
        response.status_code = 400
        response.headers['content-type'] = 'application/json'
        response._content = '{"message": "This is error"}'
        client = Client('userId', 'apiToken', 'apiSecret')
        with self.assertRaises(CatapultException) as r:
            client._check_response(response)
        err = r.exception
        self.assertEqual('400', err.code)
        self.assertEqual('This is error', err.message)
        self.assertEqual(400, err.status_code)
        self.assertEqual('Error 400: This is error', str(err))

    def test_check_response_with_plain_text_error(self):
        """
        _check_response() should extract error data from plain text
        """
        response = requests.Response()
        response.status_code = 400
        response._content = 'This is error'
        client = Client('userId', 'apiToken', 'apiSecret')
        with self.assertRaises(CatapultException) as r:
            client._check_response(response)
        err = r.exception
        self.assertEqual('400', err.code)
        self.assertEqual('This is error', err.message)
        self.assertEqual(400, err.status_code)
        self.assertEqual('Error 400: This is error', str(err))

    def test_make_request_with_json(self):
        """
        _make_request() should make request, check response and extract json data
        """
        estimated_response = requests.Response()
        estimated_response.status_code = requests.codes['ok']
        estimated_response.headers['content-type'] = 'application/json'
        estimated_response._content = '{"data": "data"}'
        with patch('requests.request', return_value = estimated_response) as p:
            client = Client('userId', 'apiToken', 'apiSecret')
            data, response, _ = client._make_request('get', '/path')
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/path', auth=('apiToken', 'apiSecret'))
            self.assertIs(estimated_response, response)
            self.assertDictEqual({'data': 'data'}, data)

    def test_make_request_with_location_header(self):
        """
        _make_request() should make request, check response and extract id from location header
        """
        estimated_response = requests.Response()
        estimated_response.status_code = requests.codes['created']
        estimated_response.headers['location'] = 'http://localhost/path/id'
        with patch('requests.request', return_value = estimated_response) as p:
            client = Client('userId', 'apiToken', 'apiSecret')
            _, response, id = client._make_request('get', '/path')
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/path', auth=('apiToken', 'apiSecret'))
            self.assertIs(estimated_response, response)
            self.assertEqual('id', id)