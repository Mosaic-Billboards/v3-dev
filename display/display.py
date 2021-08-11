#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.abspath(os.path.join('..', '/')))

import time
import tkinter as tk
from PIL import Image

from constants import image_filetypes

from dotenv import load_dotenv
load_dotenv()
WINDOW_WIDTH = os.environ.get('WINDOW_WIDTH')
WINDOW_HEIGHT = os.environ.get('WINDOW_HEIGHT')
DISPLAY_PIPE_PATH = os.environ.get('DISPLAY_PIPE_PATH')
PLAY_TIME = os.environ.get('PLAY_TIME')

from content_util import (
    create_tk_image,
    path_ext
)

display = None
pipef = None    

root = tk.Tk()

class Root_Window(object):
    def __init__(self, master, **kwargs):
        self.tk = master
        self.tk.configure(background='black')
        self.tk.title('v2-process')
        self.tk.geometry(str(WINDOW_WIDTH) + 'x' + str(WINDOW_HEIGHT))
        # self.tk.attributes('-fullscreen', True) # TODO: set fullscreen
        self.frame = tk.Frame(self.tk)
        self.frame.pack()
        self.tk.bind("<Escape>", self.end_fullscreen)

    def end_fullscreen(self, event=None):
        # self.tk.attributes('-fullscreen', False)
        os.unlink(PIPE_PATH)
        self.tk.quit()
        
# class to hold all functions to display things
class Display:
    def __init__(self):
        self.label = None
        self.current_image = None
    def display_image(self, path):
        img = Image.open(path)
        resized = img.resize((WINDOW_WIDTH, WINDOW_HEIGHT), Image.ANTIALIAS)
        self.current_image = create_tk_image(resized)
        if self.label is not None:
            self.label.configure(image=self.current_image)
            self.label.image = self.current_image
        else:
            self.label = tk.Label(root, image=self.current_image, highlightthickness=0)
        self.label.pack(expand=True)
        resized.close()
        img.close()

def handle_setup_mode(params):
    return       

def handle_live_mode(params):
    key = params[1]
    if key == 'SHOW':
        path = params[2]
        ext = path_ext(path)
        if ext in image_filetypes:
            display.display_image(path)

def handle_message(msg):
    print(f'message {msg}')
    params = str(msg).strip().split(' ')
    prefix = params[0]
    # TODO: loading screen
    # if prefix == 'SETUP_MODE': TODO: handle setup_mode
    #     handle_setup_mode(params)
    if prefix == 'LIVE_MODE':
        handle_live_mode(params)

def mainloop():
    try:
        msg = pipef.read()
        if msg:
            handle_message(msg)
    except Exception as e:
        print(f'ERROR: {e}')
        pass
    root.after(50, mainloop)

def main():
    # init display
    global display
    Root_Window(root)
    display = Display()
    
    # init pipe
    global pipef
    if os.path.exists(PIPE_PATH):
        os.unlink(PIPE_PATH)
    os.mkfifo(PIPE_PATH)
    
    # start loop
    pipe_fd = os.open(PIPE_PATH, os.O_NONBLOCK)
    with os.fdopen(pipe_fd, 'r') as pipe:
        pipef = pipe
        root.after(PLAY_TIME, mainloop)
        root.mainloop()
    exit(1)
    

if __name__ == '__main__':
    main()
        
