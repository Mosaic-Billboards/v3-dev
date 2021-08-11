#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.abspath(os.path.join('..', '/')))

import requests
import sqlite3
import json
import numpy as np
import cgi

from process_utils import (
    download_content,
    process_new_availability_number
)

from log import define_logger
logger = define_logger('JOB', __name__)

from util.api import MB_API

from dotenv import load_dotenv
load_dotenv()
BILLBOARD_ID = os.environ.get('BILLBOARD_ID')
CONTENT_PATH = os.environ.get('CONTENT_PATH')
DATABASE_PATH = os.environ.get('DATABASE_PATH')

con = None
cur = None


def _schedule_new_advertisement(ad):
    # get total number of online rotations
    cur.execute('SELECT COUNT(DISTINCT rotation) FROM schedule WHERE offline = 0 or offline = NULL')
    daily_rotations = cur.fetchone()[0]
    
    # get first online rotation number
    cur.execute('SELECT rotation FROM schedule WHERE offline = 0 or offline = NULL ORDER BY rotation ASC LIMIT 1')
    first_rotation = cur.fetchone()[0]
    
    # get distrobution interval = daily_rotations / daily_plays
    distro_interval = daily_rotations / ad.daily_plays
    num_per_rotation = 1
    
    # if distro_interval < 1, distro_interval = 1, num_per_rotation = 1/distro_interval
    if distro_interval < 1: # more plays than rotations
        distro_interval = 1 # insert in every rotation
        num_per_rotation = round(1/distro_interval, 0) # insert this many times each rotation
    distro_interval = round(distro_interval, 0)
    
    plays_left_to_insert = ad.daily_plays
    rotation_cur = first_rotation
    
    # Starting at first online rotation, skip (distro_interval # of rotations)
    # Insert num_per_rotation into openings for each rotation
    while plays_left_to_insert > 0:
        # select openings for this rotation number
        cur.execute("""
                    SELECT id, rotation, advertisement_id FROM schedule 
                    WHERE rotation = :rotation AND advertisement_id = NULL
                    """,
                    {'rotation':rotation_cur})
        rows = cur.fetchall()
        
        for i in range(len(rows)):
            if i + 1 <= num_per_rotation:
                # insert advertisement
                cur.execute('UPDATE schedule SET advertisement_id = :ad_id WHERE id = :id', 
                            {'ad_id':ad.advertisement_id, 'id':rows[i][0]})
                plays_left_to_insert = plays_left_to_insert - 1
                    
        rotation_cur = rotation_cur + distro_interval
        
    con.commit()

def _process_new_advertisement(advertisement):
    try:
        # download content from url
        filepath = download_content(advertisement['content_url'])
        
        # add path to advertisement object
        ad = Advertisement(advertisement)
        ad.content_path = filepath
        
        # write object to advertisements table
        cur.execute("""
                    INSERT INTO advertisements (advertisement_id, content_path, daily_plays, start_date, end_date, owner_created)
                    VALUES (:ad_id, :path, :plays, :start, :end, 0)
                    """, 
                    {'ad_id':ad.advertisement_id, 'path':ad.content_path, 
                    'plays':ad.daily_plays, 'start':ad.start_date, 'end':ad.end_date})
        con.commit()
        
        _schedule_new_advertisement(ad)
        process_new_availability_number()
    except Exception as e:
        logger.critical(e)
    

def _delete_advertisement(ad_id):
    try:
        # get advertisement from advertisements
        cur.execute('SELECT advertisement_id, content_path FROM advertisements WHERE advertisement_id = :ad_id LIMIT 1', {"ad_id":ad_id})
        ad = cur.fetchone()
        
        # delete content path
        content_path = ad[0][1]
        os.remove(content_path)
        
        cur.execute('UPDATE schedule SET advertisement_id = NULL WHERE advertisement_id = :ad_id', {'ad_id':ad_id})
        cur.execute('DELETE FROM advertisements WHERE advertisement_id = :ad_id', {'ad_id':ad_id})
        con.commit()
        
        process_new_availability_number()
    except Exception as e:
        logger.critical(e)
    
    
# TODO: test full process 

def process_advertisements(data):
    global con
    global cur
    
    # parse data
    data = json.loads(res.json())
    ad_ids = [ad.id for ad in data]
    
    # get all existing advertisments
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute('SELECT advertisement_id FROM advertisements WHERE owner_created = 0')
    existing_ad_ids = cur.fetchall()
    
    new_ad_ids = np.setdiff1d(ad_ids, existing_ad_ids)
    deleted_ad_ids = np.setdiff1d(existing_ad_ids, ad_ids)
    
    # process new advertisements
    for ad in data:
        if ad['id'] in new_ad_ids:
            _process_new_advertisement(ad)
        
    # delete removed advertisements
    for ext_ad in existing_ad_ids:
        if ext_ad in deleted_ad_ids:
            _delete_advertisement(ext_ad)
            
    con.commit()
    con.close()
            