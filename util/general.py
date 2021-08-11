import sys
from cosntants import DISPLAY_PIPE_PATH

def exit(status=0):
    sys.exit(status)
    
# TODO: debug when pipe file exists but display.py isn't running, open hangs
def write_display(message):
    with open(DISPLAY_PIPE_PATH, 'w') as display_pipe:
        display_pipe.write(str(message) + '\n')
    
def get_current_datetime():
    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    return utc_now

def file_read(PATH):
    if (os.path.exists(PATH)):
        with open(PATH, "r") as file:
            val = file.read()
            return val
    return None

def file_write(PATH, value):
    try:
        with open(PATH, "w") as file:
            file.write(str(value))
    except:
        logger.error('file_write error')
        pass
