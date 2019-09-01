#!/usr/bin/env python

"""
Display a png file and report the mouse position on a mouse click.
"""

import argparse
import subprocess
import tkinter as tk

from png import Png
from splice import Splice

def build_parser():
    parser = argparse.ArgumentParser(description=__doc__.strip())

    return parser


class Application():
    def __init__(self, root, canvas, in_image_filename, img, xy):
        """
        xy is an empty list object used to return with width and height.
        """
        self.root = root
        self.xy = xy
        png = Png(in_image_filename)
        image_info = png.get_header()
        self.image_width  = image_info['width']
        self.image_height = image_info['height']
        png.close()

        canvas.create_image(0, 0, anchor=tk.NW, image=img)
        canvas.bind("<Button-1>", self.callback)


    def callback(self, event):  
        print(event.x, event.y)
        x = event.x
        y = event.y
        if x >= 0 and y >= 0:
            # Return the (x,y) position to the caller.
            self.xy.append(x)
            self.xy.append(y)
            self.root.destroy()




def compute_padding(x, y, width, height):
    """
    Determine the padding needed to center the image at (x,y).
    """
    if x < width / 2:
        pad_right = 0
        pad_left = width - 2 * x
    else:
        pad_left = 0
        pad_right = 2 * x - width
    if y < height / 2:
        pad_bottom = 0
        pad_top = height - 2 * y
    else:
        pad_top = 0
        pad_bottom = 2 * y - height
    return (pad_left, pad_top, pad_right, pad_bottom)


def main(args):
    filename_png = "ball2.png"
    ret = subprocess.call(['magick', 'convert', 'ball.jpg', filename_png])
    if ret != 0:
        print('Got a subprocess.call error', ret)
        exit(ret)

    png = Png(filename_png)
    image_info = png.get_header()
    image_width  = image_info['width']
    image_height = image_info['height']

    root = tk.Tk()      
    canvas = tk.Canvas(root, width =image_width, height = image_height)
    canvas.pack()      
    # Putting the next line into __init__ causes the image to not appear.
    xy = []

    img = tk.PhotoImage(file=filename_png)
    application = Application(root, canvas, filename_png, img, xy)
    #application = Application(root, canvas, filename_png, tk.PhotoImage(file=filename_png), xy)
    tk.mainloop()
    (x, y) = xy
    (pad_left, pad_top, pad_right, pad_bottom) = compute_padding(x, y, image_width, image_height)
    print(x, y, image_width, image_height, pad_left, pad_top, pad_right, pad_bottom)


if __name__ == '__main__':
    main(build_parser().parse_args())
