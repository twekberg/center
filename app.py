#!/usr/bin/env python

"""
Display an image file and report the mouse position on a mouse click.

acen
cd ~/STUFF/N/O/SPELLSNO/IMAGES/BIG  
~/src/center/app.py -i 00SPREAD -o 00SPREAD-CENTER -t TMP
"""

import os
import os.path
import argparse
import sys
import subprocess
import time
import tkinter as tk

from get_image_info import get_image_size
from splice import Splice

def build_parser():
    parser = argparse.ArgumentParser(description=__doc__.strip())

    parser.add_argument('-i', '--in_dir',
                        default='tests/in',
                        help='Input directory. Default: %(default)s.')
    parser.add_argument('-o', '--out_dir',
                        default='tests/out',
                        help='Output directory. Default: %(default)s.')
    parser.add_argument('-t', '--tmp_dir',
                        default='tests/tmp',
                        help='Temp directory. Default: %(default)s.')

    return parser


class Application():
    def __init__(self, root, canvas, source_image_filename, in_image_filename, out_image_filename, img, scale_factor):
        self.root = root
        self.canvas = canvas
        self.source_image_filename = source_image_filename
        self.in_image_filename = in_image_filename
        self.out_image_filename = out_image_filename
        self.scale_factor = scale_factor
        
        (self.image_width, self.image_height) = get_image_size(in_image_filename)
        (self.source_image_width, self.source_image_height) = get_image_size(source_image_filename)

        canvas.create_image(0, 0, anchor=tk.NW, image=img)
        canvas.bind("<Button-1>", self.callback)
        canvas.bind("<Button-3>", sys.exit)


    def callback(self, event):  
        # Need to /100 because the scale_factor is a percentage.
        self.x = round(event.x / (int(self.scale_factor)/100))
        self.y = round(event.y / (int(self.scale_factor)/100))
        print('TWE In callback', self.scale_factor, (self.x, self.y),(event.x, event.y))
        if self.x >= 0 and self.y >= 0:
            self.canvas.unbind("<Button-1>")
            self.root.destroy()


    def process_image(self):
        (pad_left, pad_top, pad_right, pad_bottom) = compute_padding(self.x, self.y, self.source_image_width, self.source_image_height)
        left_side = pad_left or pad_right
        top_side = pad_top or pad_bottom
        sides = []
        for (pad, side) in [(pad_left, 'left'), (pad_top, 'top'), (pad_right, 'right'), (pad_bottom, 'bottom')]:
            if pad:
                sides.append(side)
        s = Splice(self.source_image_filename, self.out_image_filename)
        s.action(sides, left_side, top_side)
        


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


def add_to_clipboard(text):
    """
    Put the text in the clipboard, removing whitespace from either end. What actually
    happens is that an extra character is appended to the clipboard which needs to be
    deleted to get the text.
    """
    command = 'echo "' + text.strip() + '"| /cygdrive/c/Windows/System32/clip.exe'
    os.system(command)


def main(args):
    out_filenames = os.listdir(args.out_dir)
    in_filenames  = os.listdir(args.in_dir)
    n_file = 0
    for in_filename in in_filenames:
        n_file += 1
        if in_filename in out_filenames:
            continue
        in_filename_path = os.path.join(args.in_dir, in_filename)
        # Put in clipboard in case a transform is needed or the image got an error.
        root = tk.Tk()
        png_filename_path = os.path.join(args.tmp_dir, in_filename[0:-3] + 'png')
        (image_width, image_height) = get_image_size(in_filename_path)

        # Scale the source image to make it fit within the screen. Small images get enlarged.
        # Reduce screen height for window title and space used at the bottom of the screen.
        screen_height = root.winfo_screenheight() - 100
        # There is plenty of screen width. Base scale factor on the smaller height.
        # > 1 -> enlarge, < 1 -> shrink.
        scale_factor = '%1.0f' % (screen_height / image_height * 100,)

        print('%d/%d %s ih=%s, %s%%' % (n_file, len(in_filenames), in_filename, image_height, scale_factor))
        if image_height <= 1:
            print('-------------------------------------------------------------------------------')
            print('Bad image height. Use GIMP to re-export this image as a GIF.')
            add_to_clipboard(in_filename)
            continue
        cmd = ['magick', 'convert', in_filename_path,
               '-resize', scale_factor+'%',
               png_filename_path]
        ret = subprocess.call(cmd)
        if ret != 0:
            raise Exception('Got a subprocess.call error %s, command=%s' % (ret,' '.join(cmd)))
        (image_width, image_height) = get_image_size(png_filename_path)

        canvas = tk.Canvas(root, width =image_width, height = image_height)
        canvas.pack()      
        # Putting the next line into __init__ causes the image to not appear.

        out_filename_path = os.path.join(args.out_dir, in_filename)
        img = tk.PhotoImage(master=canvas, file=png_filename_path)
        application = Application(root, canvas, os.path.join(args.in_dir, in_filename),
                                  png_filename_path, out_filename_path, img, scale_factor)
        #application = Application(root, canvas, png_filename_path, tk.PhotoImage(file=png_filename_path))
        tk.mainloop()
        add_to_clipboard(in_filename)
        application.process_image()
        os.remove(png_filename_path)
        time.sleep(1)


if __name__ == '__main__':
    main(build_parser().parse_args())
