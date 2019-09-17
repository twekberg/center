#!/usr/bin/env python
"""
Display a png file and report the mouse position on a mouse click.
"""

0 # Prevent string concatenation

"""
for left in 'left' 'right' ''; do
   for top in 'top' 'bottom' ''; do
     if [ "$left$top" != "" ]; then
       echo "./splice.py -s $left $top"
       ./splice.py -s $left $top
     fi
   done
done
"""

from png import Png
import argparse
from datetime import datetime
import subprocess
import tkinter as tk

in_image_filename = 'ball.png'
out_image_filename = 'ball-splice-left.png'

# Keep this around for a while.
# When this turns into a full class remove this and the 2 filenames above.
def build_parser():
    parser = argparse.ArgumentParser(description=__doc__.strip())

    parser.add_argument('-l', '--left_size', type=int,
                        default=100,
                        help='When there is a left or right border, use this number of pixels.')
    parser.add_argument('-t', '--top_size', type=int,
                        default=200,
                        help='When there is a top or bottom border, use this number of pixels.')
    parser.add_argument('-s', '--sides', nargs='+', choices=['left', 'right', 'top', 'bottom'],
                        default='left',
                        help='The year to search. Default: %(default)s.')

    return parser

class Splice():
    def __init__(self, in_image_filename, out_image_filename):
        self.in_image_filename = in_image_filename
        self.out_image_filename = out_image_filename
        png = Png(self.in_image_filename)
        image_info = png.get_header()
        self.image_width  = image_info['width']
        self.image_height = image_info['height']
        png.close()

    def get_wh(self):
        return (self.image_width, self.image_height)

    def action(self, sides, left_size, top_size):
        splice_arg = None
        side_code = ''.join([side[0].upper() for side in ['left', 'top', 'right', 'bottom'] if side in sides])
        if side_code == 'L':
            splice_arg = '%sx0' % left_size
        elif side_code == 'T':
            splice_arg = '0x%s' % top_size
        elif side_code == 'R':
            splice_arg = '%sx0+%s+0' % (left_size, self.image_width)
        elif side_code == 'B':
            splice_arg = '0x%s+0+%s' % (top_size, self.image_height)
        elif side_code == 'LT':
            splice_arg = '%sx%s' % (left_size, top_size)
        elif side_code == 'LB': # Need to determine the next for splice_args
            splice_arg = '%sx%s+0+%s' % (left_size, top_size, self.image_height)
        elif side_code == 'TR':
            splice_arg = '%sx%s+%s+0' % (left_size, top_size, self.image_width)
        elif side_code == 'RB':
            splice_arg = '%sx%s+%s+%s' % (left_size, top_size, self.image_width, self.image_height)
        if splice_arg:
            ret = subprocess.call(['magick', 'convert', self.in_image_filename,
                                   '-background', 'black',
                                   '-splice', splice_arg,
                                   self.out_image_filename])
            if ret != 0:
                print('Got a subprocess.call error', ret)
                exit(ret)
        else:
            print('Unknown side')


def main(args):
    splice = Splice(in_image_filename, out_image_filename)
    splice.action(args.sides, args.left_size, args.top_size)
    (image_width, image_height) = splice.get_wh()
    root = tk.Tk()
    canvas = tk.Canvas(root,
                       width = image_width + (args.left_size if 'left' in args.sides else 0)
                       + (args.left_size if 'right' in args.sides else 0),
                       height = image_height + (args.top_size if 'top' in args.sides else 0)
                       + (args.top_size if 'bottom' in args.sides else 0))
    canvas.pack()
    img = tk.PhotoImage(file=out_image_filename)
    canvas.create_image(0, 0, anchor=tk.NW, image=img)

    canvas.bind("<Button-1>", callback)

    tk.mainloop()

def callback(event):
    x = event.x
    y = event.y
    if x >= 0 and y >= 0:
        print("clicked at: ", x, y)


if __name__ == '__main__':
    main(build_parser().parse_args())
