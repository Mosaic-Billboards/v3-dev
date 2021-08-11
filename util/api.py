import sys, os
sys.path.append(os.path.abspath(os.path.join('..', '/')))

import requests
from requests.exceptions import HTTPError

from log import define_logger
logger = define_logger('API', __name__)

from dotenv import load_dotenv
load_dotenv()

class MB_API:
    def __init__(self):
        self.base_url = "https://localhost:3000/api/billboard"
        self.BILLBOARD_ID = os.environ.get('BILLBOARD_ID')
        self.TOKEN = os.environ.get('AUTH_TOKEN')    
        
    def _request_api(uri):
        headers = {"content-type": "application/json; charset=UTF-8", 'Authorization':f'Bearer {self.TOKEN}'}
        res = requests.get(uri, headers=headers)
        
        try:
            resp.raise_for_status()
        except HTTPError as e:
            logger.critical(e, resp.text)
            return None
        
        data = res.json()
        return data
        
    def ping(self):
        endpoint = self.base_url + '/ping' + '?id=' + self.BILLBOARD_ID
        self._request_api(endpoint)
    
    def check_firmware(self):
        endpoint = self.base_url + '/firmware' + '?id=' + self.BILLBOARD_ID
        res = self._request_api(endpoint)
        saved_ver = os.environ.get('FIRMWARE_VERSION')
        if res == saved_ver:
            return None
        # TODO download new firmware version
        return res
    
    def fetch_ads(self):
        endpoint = self.base_url + '/live-advertisements' + '?id=' + self.BILLBOARD_ID
        res = self._request_api(endpoint)
        if len(res) > 0:
            return res
        return None
    
    def fetch_owner_ads(self):
        endpoint = self.base_url + '/owner-advertisements' + '?id=' + self.BILLBOARD_ID
        res = self._request_api(endpoint)
        if len(res) > 0:
            return res
        return None
    
    def set_availability(self, total, available):
        endpoint = self.base_url + '/availability' + f'?id={self.BILLBOARD_ID}&total={total}&available={available}'
        res = self._request_api(endpoint)
            

    
