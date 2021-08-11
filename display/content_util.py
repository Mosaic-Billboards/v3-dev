import sys, os
sys.path.append(os.path.abspath(os.path.join('..', '/')))

from PIL import ImageTk, Image, ImageDraw, ImageFont

def path_ext(path):
    words = str(path).split('.')
    ext = words[len(words) - 1].strip()
    return ext

def create_tk_image(img):
    image = ImageTk.PhotoImage(image=img)
    print('created tk image')
    return image