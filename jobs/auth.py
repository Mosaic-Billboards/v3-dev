#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.abspath(os.path.join('..', '/')))

import json
import firebase_admin
import requests
from requests.exceptions import HTTPError
import subprocess as sp

from creds import (
    retrieve_user_email,
    retrieve_user_password
)

API_KEY = "AIzaSyDNyQyZF2P7Rn6lOzYOKh-UHB5YPdWOb_I"
FIREBASE_REST_API = "https://identitytoolkit.googleapis.com/v1/accounts"

def main():
    email = retrieve_user_email()
    password = retrieve_user_password()
    if email is not None and password is not None:
        
        request_url = "%s:signInWithPassword?key=%s" % (FIREBASE_REST_API, API_KEY)
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"email": email, "password": password, "returnSecureToken": True})
    
        resp = requests.post(request_url, headers=headers, data=data)
        
        try:
            resp.raise_for_status()
        except HTTPError as e:
            raise HTTPError(e, resp.text)
            
        data = resp.json()
        if data['idToken']:
            token = data['idToken']
            sp.run(f'dotenv set AUTH_TOKEN {token}')
            
        

if __name__ == '__main__':
    main()