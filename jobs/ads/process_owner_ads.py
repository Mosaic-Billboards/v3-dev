#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.abspath(os.path.join('..', '/')))

import sqlite3
import json

from process_utils import (
    download_content,
    process_new_availability_number
)

from log import define_logger
logger = define_logger('JOB', __name__)

from dotenv import load_dotenv
load_dotenv()
DATABASE_PATH = os.environ.get('DATABASE_PATH')

con = None
cur = None

def _process_new_owner_advertisement(ad):
    try:
        # download content from url
        filepath = download_content(advertisement['content_url'])
        
        # add path to advertisement object
        ad = Advertisement(advertisement)
        ad.content_path = filepath
        
        # write object to advertisements table
        cur.execute("""
                    INSERT INTO advertisements (advertisement_id, content_path, owner_created)
                    VALUES (:ad_id, :path, 1)
                    """, 
                    {'ad_id':ad.advertisement_id, 'path':ad.content_path})
        con.commit()
        
        process_new_availability_number()
    except Exception as e:
        logger.critical(e)
    
    
def _delete_owner_advertisement(ad_id):
    try:
        # get advertisement from advertisements
        cur.execute('SELECT advertisement_id, content_path FROM advertisements WHERE advertisement_id = :ad_id LIMIT 1', {"ad_id":ad_id})
        ad = cur.fetchone()
        
        # delete content path
        content_path = ad[0][1]
        os.remove(content_path)
        
        cur.execute('DELETE FROM advertisements WHERE advertisement_id = :ad_id', {'ad_id':ad_id})
        con.commit()
        
        process_new_availability_number()
    except Exception as e:
        logger.critical(e)


def process_owner_advertisements(data):
    global con
    global cur
    
    # parse data
    data = json.loads(res.json())
    ad_ids = [ad.id for ad in data]
    
    # get all existing advertisments
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute('SELECT advertisement_id FROM advertisements WHERE owner_created = 1')
    existing_ad_ids = cur.fetchall()
    
    new_ad_ids = np.setdiff1d(ad_ids, existing_ad_ids)
    deleted_ad_ids = np.setdiff1d(existing_ad_ids, ad_ids)
    
    # process new advertisements
    for ad in data:
        if ad['id'] in new_ad_ids:
            _process_new_owner_advertisement(ad)
        
    # delete removed advertisements
    for ext_ad in existing_ad_ids:
        if ext_ad in deleted_ad_ids:
            _delete_owner_advertisement(ext_ad)
    
    con.commit()
    con.close()