import os
import logging
from dotenv import load_dotenv
load_dotenv()
LOG_FILE_PATH = os.environ.get('LOG_FILE_PATH')

def define_logger(mode_name, file_name):
    logger = logging.getLogger(mode_name + ' - ' + name)
    logger.setLevel(logging.DEBUG)

    logHandler = logging.StreamHandler()
    filelogHandler = logging.FileHandler(LOG_FILE_PATH)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logHandler.setFormatter(formatter)
    filelogHandler.setFormatter(formatter)

    logger.addHandler(filelogHandler)
    logger.addHandler(logHandler)

    return logger