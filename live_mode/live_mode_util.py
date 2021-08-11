
import sqlite3
from datetime import datetime

import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_PATH = os.environ.get('DATABASE_PATH')

def get_current_rotation():
    now = datetime.datetime.now()
    sec_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    return round(sec_since_midnight / 80)
    
    
def get_rotation_items(rotation):
    rot_items = []
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("SELECT rotation, play, advertisement_id FROM schedule WHERE rotation = :rotation", {'rotation':rotation})
    for item in cur.fetchall():
        if item[2] is not None:
            cur.execute('SELECT content_path FROM advertisements WHERE advertisement_id = :ad_id LIMIT 1', {'ad_id': item[2]})
            content_path = cur.fetchone()[0]
            rot_items.add(content_path)
        else:
            # TODO: get next default owner image
            owner_content_path
            rot_items.add(owner_content_path)
    con.close()
    return rot_items