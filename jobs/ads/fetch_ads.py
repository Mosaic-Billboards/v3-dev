#!/usr/bin/env python3

# fetch_ads.py --> request endpoint, get current ads, hand to process_advertisements

import sys, os
sys.path.append(os.path.abspath(os.path.join('..', '/')))

from log import define_logger
logger = define_logger('JOB', __name__)

import json
from util.api import MB_API
from process_ads import process_advertisements

if __name__ == "__main__":
    try:
        api = MB_API()
        res = api.fetch_ads()
        if res is not None:
            process_advertisements(data)
        sys.exit(0)
    except Exception as e:
        logger.critical(e)
        sys.exit(1)