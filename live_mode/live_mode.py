#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.abspath(os.path.join('..', '/')))

import sqlite3
from datetime import datetime
import pytz
import time

from util.general import get_current_datetime, write_display

from dotenv import load_dotenv
load_dotenv()
DATABASE_PATH = os.environ.get('DATABASE_PATH')
DISPLAY_PIPE_PATH = os.environ.get('DISPLAY_PIPE_PATH')
PLAY_TIME = os.environ.get('PLAY_TIME')

from util.database import create_database
from util.general import write_display

from log import define_logger
logger = define_logger('LIVE_MODE', __name__)

con = None
cur = None

# -------------------------------
# QUERIES
# -------------------------------

def live_mode_init():
    if not os.path.exists(DATABASE_PATH):
        create_database()

rotation = 0
play = 0
items = []

def live_mode_mainloop():
    # get current rotation
    global con
    global cur
    global rotation
    global play
    global items
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    rotation = get_current_rotation()
    while os.path.exists(DISPLAY_PIPE_PATH):
        if play > 9:
            rotation = get_current_rotation()
            items = get_rotation_items(rotation)
            play = 0
        content = items[play]
        command = f'LIVE_MODE SHOW {content}'
        write_display(command)
        play = play + 1
        time.sleep(8)
    while not os.path.exists(DATABASE_PATH):
        time.sleep(1)
    live_mode_mainloop()

if __name__ == '__main__':
    live_mode_init()
    live_mode_mainloop()