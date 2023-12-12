import requests
import json
import os

class TwitchAPI:
    def __init__(self):
        self.base_url = 'https://api.twitch.tv/helix/'
        self.client_id = os.environ['CLIENT_ID']
        self.client_secret = os.environ['CLIENT_SECRET']
        self.headers = {'Client-ID': self.client_id, 'Authorization': f'Bearer {self.get_access_token()}'}
        self.broadcaster_id = 1001457687

    def get_access_token(self):
        url = 'https://id.twitch.tv/oauth2/token'
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        response = requests.post(url, params=params)
        return response.json()['access_token']

    def get_user_info(self, login_name):
        url = self.base_url + 'users'
        params = {'login': login_name}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_streams(self, user_id=None):
        url = self.base_url + 'streams'
        params = {}
        if user_id:
            params['user_id'] = user_id
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()
    
    def check_user_follows(self, from_id, to_id):
        url = self.base_url + 'users/follows'
        params = {'from_id': from_id, 'to_id': to_id}
        response = requests.get(url, headers=self.headers, params=params)
        data = response.json()
        return True
    
    def create_clip(self):
        url = self.base_url + 'clips'
        headers = self.headers
        body = {
            'broadcaster_id': self.broadcaster_id
        }
        response = requests.post(url, headers=headers, json=body)
        return response.json()

