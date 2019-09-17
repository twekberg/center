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
    def __init__(self, root, canvas, in_image_filename, out_image_filename, img):
        self.root = root
        self.in_image_filename = in_image_filename
        self.out_image_filename = out_image_filename
        
        png = Png(in_image_filename)
        image_info = png.get_header()
        self.image_width  = image_info['width']
        self.image_height = image_info['height']
        png.close()

        canvas.create_image(0, 0, anchor=tk.NW, image=img)
        canvas.bind("<Button-1>", self.callback)


    def callback(self, event):  
        self.x = event.x
        self.y = event.y
        if self.x >= 0 and self.y >= 0:
            self.root.destroy()


    def process_image(self):
        (pad_left, pad_top, pad_right, pad_bottom) = compute_padding(self.x, self.y, self.image_width, self.image_height)
        left_size = pad_left or pad_right
        top_size = padtop or pad_bottom
        sides = []
        for (pad, side) in [(pad_left, 'left'), (pad_top, 'top'), (pad_right, 'right'), (pad_bottom, 'bottom')]:
            if pad:
                sidex.append(side)
        s = Splice(self.in_image_filename, self.out_image_filename)
        s.action(sides, left_side, top_side)
        print(self.x, self.y, self.image_width, self.image_height, pad_left, pad_top, pad_right, pad_bottom)
        


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
    out_filename_png = "ball2.png"
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

    img = tk.PhotoImage(file=filename_png)
    application = Application(root, canvas, filename_png, out_filename_png, img)
    #application = Application(root, canvas, filename_png, tk.PhotoImage(file=filename_png))
    tk.mainloop()
    application.process_image()


if __name__ == '__main__':
    main(build_parser().parse_args())
