from typing import List, Optional, Dict
import requests


class ProsperAPI:
    """A client for accessing the Prosper Investor API.

    Docs can be found here: https://developers.prosper.com/docs/investor/
    """

    @classmethod
    def get_client_by_username_password(
        cls,
        client_id : str,
        client_secret : str,
        username : str,
        password :str
    ):
        """Initialize the api client via the password auth flow."""
        client = ProsperAPI()
        client.acquire_token_by_username_password(client_id, client_secret, username, password)
        return client

    def __init__(self):
        """Initialize the Prosper API Client."""
        self._token : Optional[str] = None
        self._prosper_base_address = 'https://api.prosper.com/v1/'

    def account(self) -> Dict:
        """Return a summary of the account."""
        accounts = self.get('accounts/prosper/')
        return accounts.json()

    def notes(self) -> List[Dict]:
        """Return a generator for all of the accounts notes."""
        offset = 0
        limit = 100 # max is 100 as specified in prosper docs.

        while True:
            response = self.get('notes/', params={
                'offset': offset,
                'limit': limit
            })

            results = response.json()
            for note in results['result']:
                yield note

            offset += results['result_count']
            if offset >= results['total_count']:
                break

    def payments(self) -> List[Dict]:
        """All payments for all notes in the account for past 90 days."""
        notes = self.notes()
        return self.payments_by_loan_number([
            note['loan_number']
            for note in notes
        ])

    def listings(
        self,
        include_only_bidable : bool = True,
        include_only_invested : Optional[bool] = None
    ):
        """Return Prosper loan listings

        Note: Getting the listings that you have already invested in is sort of tricky /
        possibly impossible in the case of charged-off loans.

        To get listings that you have already invested in, you need to query with
        include_only_invested=True and include_only_bidable=False. However, this
        seems to only return listings that are not charged-off or sold because once
        the debt is sold you "don't own" it anymore. Practically speaking this is not
        very helpful for evaluating your portfolio.

        """
        return self._fetch_listings(
            include_only_biddable=include_only_bidable,
            include_only_invested=include_only_invested,
            )

    def _fetch_listings(
        self,
        include_only_biddable : bool = True,
        include_only_invested : Optional[bool] = None,
        include_credit_bureau_data : bool = False
    ):
        """Fetch listings from the prosper API."""

        include_credit_bureau_values = None
        if include_credit_bureau_data:
            include_credit_bureau_values = 'experian,transunion'

        limit = 100
        offset = 0
        while True:
            response = self.get('listingsvc/v2/listings', params={
                'limit': limit,
                'offset': offset,
                'include_credit_bureau_values': include_credit_bureau_values,
                'biddable': include_only_biddable,
                'invested': include_only_invested
            })

            results = response.json()
            for payment in results['result']:
                yield payment

            offset += results['result_count']
            if offset >= results['total_count']:
                break


    def payments_by_loan_number(self, loan_numbers : List[int]) -> Dict[int, List[Dict]]:
        """Return payments for a list of loan ids

        From the prosper API docs:
            The payments API allows you to retrieve the payment history on a
            single loan, or a list of loans that you own. If you have purchased a
            Note on the loan, the payments API will return historical payment
            history on your pro-rata portion of the loan.
            (https://developers.prosper.com/docs/investor/payments-api/)
        """

        # The maximum number of unique loan_numbers allowed per request is 25
        chunk_size = 25
        loan_number_chunks = [
            loan_numbers[i:i + chunk_size]
            for i in range(0, len(loan_numbers), chunk_size)
        ]

        for loan_number_chunk in loan_number_chunks:
            for payment in self._fetch_payments_by_loan_number(loan_number_chunk):
                yield payment

    def _fetch_payments_by_loan_number(self, loan_numbers : List[int]) -> Dict[int, List[Dict]]:
        """Fetch payments for the past 90 days.

        TODO: Possibly modify this endpoint to allow querying for older payments.
        """
        if len(loan_numbers) > 25:
            raise Exception('Requests for payments must be chunked into 25 loans or less.')

        loan_numbers = ','.join([
            str(loan_id)
            for loan_id in loan_numbers
        ])

        limit = 100
        offset = 0
        while True:
            response = self.get('loans/payments/', params={
                'loan_number': loan_numbers,
                'limit': limit,
                'offset': offset
            })

            results = response.json()
            for payment in results['result']:
                yield payment

            offset += results['result_count']
            if offset >= results['total_count']:
                break

    def acquire_token_by_username_password(
        self,
        client_id : str,
        client_secret : str,
        username : str,
        password : str
    ):
        """Acquire a prosper OAuth2 access token via password flow."""
        url = self._prosper_base_address + "security/oauth/token"
        data = dict(
            grant_type='password',
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password
        )

        result = requests.post(url, data=data)
        if result.status_code != 200:
            raise Exception("Could not acquire token.")

        auth = result.json()
        self._token = auth['access_token']

    def get(self, url : str, params : Optional[Dict[str,str]] = None):
        """Perform an authenticated GET request."""
        full_url = '%s%s' % (
            self._prosper_base_address,
            url
        )
        return requests.get(full_url, params, headers=self.get_headers())

    def get_token(self) -> str:
        """Return a auth token."""
        if not self._token:
            raise Exception(
                'You must authenticate the client before attempting to make requests. '
                'Try calling `acquire_token_by_username_password`.')
        return self._token

    def get_headers(self) -> Dict[str, str]:
        """Get headers needed to make requests of Prosper's API."""
        return {
           'Authorization': 'bearer %s' % self.get_token(),
           'Accept': 'application/json'
        }
