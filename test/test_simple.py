import unittest
from funkload.FunkLoadTestCase import FunkLoadTestCase
from funkload.utils import extract_token

class Simple(FunkLoadTestCase):
    def setUp(self):
        self.server_url = self.conf_get('main', 'url')
   
    def test_simple(self):
        server_url = self.server_url
        reply = self.get(server_url + '/auth/login', description='GET /auth/login')
        csrftoken = extract_token(self.getBody(), 'name="csrf_token" type="hidden" value="', '">').strip()
        self.post(server_url + '/auth/login', params=[
            ['csrf_token', csrftoken],
            ['username', '123'],
            ['password', '123']
        ], description='POST /auth/login')

        reply = self.get(server_url + '/album/search', description='GET /album/search')
        csrftoken = extract_token(self.getBody(), 'name="csrf_token" type="hidden" value="', '">').strip()
        self.post(server_url + '/album/search', params=[
             ['csrf_token', csrftoken],
             ['tags', 'europe']
        ], description='POST /album/search')

if __name__ in ('main', '__main__'):
    unittest.main()
