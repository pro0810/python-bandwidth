import unittest
import six

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth import client, client_classes

class ClientTests(unittest.TestCase):
    def test_call_with_supported_client(self):
        """
        Call of client() should return client instance for supported client name
        """
        self.assertIsNotNone(client('catapult', 'userId', 'token', 'secret'))

    def test_call_with_supported_client_different_case(self):
        """
        Call of client() should return client instance for supported client name (case insensitive)
        """
        self.assertIsNotNone(client('CAtapult', 'userId', 'token', 'secret'))

    @unittest.expectedFailure
    def test_call_with_unsupported_client(self):
        """
        Call of client() should raise error for unsupported client name
        """
        client('Non existing client')

    def test_call_with_caching_client_class_name(self):
        """
        Call of client() should cache client class name
        """
        client_classes = {}
        orig_import = __import__
        with patch('__builtin__.__import__', side_effect=orig_import) as p:
            client('catapult', 'userId', 'token', 'secret')
            p.assert_called_once_with('bandwidth.catapult')
            client('catapult', 'userId', 'token', 'secret')
            p.assert_called_once_with('bandwidth.catapult')

