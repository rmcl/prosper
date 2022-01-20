from unittest import TestCase
from unittest.mock import Mock, patch

from prosper.api import ProsperAPI


class ProsperAPITestCase(TestCase):

    def setUp(self):
        self.client = ProsperAPI()
        self.client._token = 'TOKEN'

    def test_account(self):
        """Test that we make a request to get account information."""

        with patch('prosper.api.requests') as patch_request:
            patch_request.get.return_value.json.return_value = {'HELLO': 'WORLD!'}

            result = self.client.account()
            self.assertEqual(result, {
                'HELLO': 'WORLD!'
            })

            patch_request.get.assert_called_once_with(
                'https://api.prosper.com/v1/accounts/prosper/',
                None,
                headers={
                    'Authorization': 'bearer TOKEN',
                    'Accept': 'application/json'
                })
