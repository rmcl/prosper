import json
import requests


class ProsperAPI:
    
    @classmethod
    def get_client_by_username_password(cls, client_id, client_secret, username, password):
        client = ProsperAPI()
        client.acquire_token_by_username_password(client_id, client_secret, username, password)
        return client
    
    def __init__(self):
        '''
        
        For most APIs, including our security API for requesting access/refresh tokens, the <prosper_base_address> is` https://api.prosper.com/v1. The exception to this is the listings API, where the <prosper_base_address> is https://api.prosper.com/
        '''
        self._prosper_base_address = 'https://api.prosper.com/v1/'
    
    def account(self):
        accounts = self.get('accounts/prosper/')
        return accounts.json()
    
    def list_notes(self):
        offset = 0
        limit = 100 # max is 100 as specified in prosper docs.
        
        while True:
            print('performing reuqest', offset, limit)
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

    def acquire_token_by_username_password(self, client_id, client_secret, username, password):
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
        self._token_type = auth['token_type']
        self._token = auth['access_token']
    
    def get(self, url, params = None):
        full_url = '%s%s' % (
            self._prosper_base_address,
            url
        )
        return requests.get(full_url, params, headers=self.get_headers())
    
    def get_token(self):
        return self._token
        
    def get_headers(self):
        return {
           'Authorization': 'bearer %s' % self.get_token(),
           'Accept': 'application/json'
        }
   