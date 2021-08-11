#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.abspath(os.path.join('..', '/')))

import sqlite3

from dotenv import load_dotenv
load_dotenv()
DATABASE_PATH = os.environ.get('DATABASE_PATH')

create_schedule_table_query = """
CREATE TABLE schedule (
    id INT,
    rotation INT,
    play INT,
    advertisement_id TEXT,
    offline INT,
);
"""

create_advertisements_table_query = """
CREATE TABLE advertisements (
    advertisement_id INT,
    content_url TEXT,
    content_path TEXT,
    daily_plays INT,
    start_date TEXT,
    end_date TEXT,
    owner_created INT,
);
"""

def create_database():
    global con
    global cur
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    
    # create tables
    cur.execute(create_schedule_table_query)
    cur.execute(create_advertisements_table_query)
    
    # build empty schedule
    total_rows = 10800
    rotation = 0
    play = 0
    offline = 1
    for i in range(total_rows):
        if i > 3600:
            offline = 0
        if play > 9:
            rotation = rotation + 1
            play = 0
        cur.execute("""
                    INSERT INTO schedule (id, rotation, play, advertisement_id, offline) 
                    VALUES (:id, :rotation, :play, :advertisement_id, :offline)
                    """, {'id':i, 'rotation':rotation, 'play':play,
                    'advertisement_id': None, 'offline':offline})
        play = play + 1
    
    con.commit()