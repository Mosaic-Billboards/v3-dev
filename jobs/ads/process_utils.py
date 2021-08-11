#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.abspath(os.path.join('..', '/')))

import sqlite3
import requests
import cgi

from log import define_logger
logger = define_logger('JOB', __name__)

from util.api import MB_API

from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.environ.get('DATABASE_URL')

class Advertisement:
    def __init__(self, ad):
        self.advertisement_id = ad.advertisement_id
        self.content_url = ad.content_url
        self.content_path = None
        self.daily_plays = ad.daily_plays
        self.start_date = ad.start_date
        self.end_date = ad.end_date
    @property
    def content_path(self):
        return self.content_path
    @setter
    def content_path(self, path):
        self.content_path = path

def download_content(ad_id, url):
    filepath = None
    try:
        r = requests.get(url, stream=True)
        mimetype, options = cgi.parse_headers(r.headers['Content-Type'])
        maintype, ext = mimetype.split('/')
        filepath = os.path.join(CONTENT_PATH, f'{ad_id}.{ext}')
        chunk_size = 1024
        if maintype == 'video':
            chunk_size = 1024 * 1024
        with open(filepath, 'wb') as file:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    file.write(chunk)
        return filepath
    except:
        logger.error(f'ERROR downloading content for {ad_id}')
        return filepath
    
def process_new_availability_number():
    con = sqlite3.connect(DATABASE_URL)
    cur = con.cursor()
    
    # add up daily plays of all ads in advertisements
    cur.execute('SELECT SUM(daily_plays) FROM advertisements GROUP BY advertisement_id')
    total_used_plays = cur.fetchone()[0]
    
    # calculate total plays per day
    cur.execute('SELECT COUNT(DISTINCT rotation) FROM schedule WHERE offline = 0 or offline = NULL')
    total_plays = cur.fetchone()[0] * 10
    
    available_plays = total_plays - total_used_plays
    
    api = MB_API()
    api.set_availability(total_plays, available_plays)
    
    con.commit()
    con.close()
    