#!/usr/bin/env python

"""
Similar to app-move except this displays a montage of images instead
of one image at a time. Hopefully this will be faster. The mouse commands
are:
Left - select an image
Middle - move to the next montage.
Right - stop
"""
#
r"""
todo:

done:
Did some more testing. Looks good.

Decided not to change the logic for continue_filename. Move it out of
callbacks and put it into the main loop. It is the last file in a
batch.

The selected file can be written to out_filename.

Mapped image number determined by (x,y) point to the corresponding  image file.

Added logic for the mouse callbacks as noted above.

Wrote function that calculates the UL and LR corners.
The left mouse click selects the right rectangle.

Formulae for upper left and lower right coordinates
Upper Left:  (11+220*n, 11+242*n)
Lower Right: (212+220.3*n, 230+242*n)
Displayed the image in gimp to determine the point positions

Displays args.n_images images in a montag.
The images are all the same size so it looks like a grid.


montage -label '%t\n%[width]x%[height]' \
          -size 512x512 '../img_photos/*_orig.*[120x90]' -auto-orient \
          -geometry +5+5 -tile 5x  -frame 5  -shadow  photo_index.html

acen
cd ~/STUFF/N/O/SPELLSNO/IMAGES/BIG
~/src/center/app.py -i 00SPREAD -o 00SPREAD-CENTER -t TMP

The operative command to be run eventually is this:
In this directory:
  E:\cygwin64\home\Tom Ekberg\STUFF\N\O\SPELLSNO\IMAGES\BIG>
Run this:
mklink 00CRAB\0_822.lnk "e:\cygwin64\home\Tom Ekberg\STUFF\N\O\SPELLSNO\IMAGES\BIG\00SPREAD\0_822.jpg"

where 0_822 is the base name of a file. There may be other file types.
"""

import glob
import os
import os.path
import argparse
import sys
import subprocess
import time
import tkinter as tk

from get_image_info import get_image_size

def build_parser():
    parser = argparse.ArgumentParser(description=__doc__.strip())

    parser.add_argument('-i', '--in_dir',
                        default='tests/in',
                        help='Input directory. Default: %(default)s.')
#                        default='00CRAB',

    parser.add_argument('-a', '--alt_in_dir',
                        default='tests/alt_in',
                        help='Alternate input directory for .lnk files. Default: %(default)s.')
#                        default='00SPREAD',

    parser.add_argument('-c', '--continue_filename',
                        default='tests/spread-continue.txt',
                        help='Filename that contains the last file processed. '
                        'Default: %(default)s.')

    parser.add_argument('-s', '--thumb_size', type=int,
                        default=200,
                        help='Width and height of each thumbnail. '
                        'Default: %(default)s.')
                        
    parser.add_argument('-n', '--n_rows', type=int,
                        default=3,
                        help='Number of thumbnail rows in a montage. '
                        'Default: %(default)s.')

    
    parser.add_argument('-r', '--row_size', type=int,
                        default=5,
                        help='Number of images per row. '
                        'Default: %(default)s.')

    parser.add_argument('-o', '--out_filename',
                        default='tests/spread-images.txt',
                        help='Output filename for the filenames that were selected. '
                        'Default: %(default)s.')

    parser.add_argument('-t', '--tmp_dir',
                        default='tests/tmp',
                        help='Temp directory. Default: %(default)s.')
#                        default='TMP',

    return parser


class Application():
    def __init__(self, args, root, canvas, source_image_filename, in_image_filename, img,
                 rect_points):
        self.root = root
        self.canvas = canvas
        self.source_image_filename = source_image_filename
        self.in_image_filename = in_image_filename
        self.out_filename = args.out_filename
        self.thumb_size = args.thumb_size
        self.continue_filename = args.continue_filename
        (self.image_width, self.image_height) = get_image_size(in_image_filename)
        (self.source_image_width, self.source_image_height) = get_image_size(source_image_filename)
        self.rect_points = rect_points
        canvas.create_image(0, 0, anchor=tk.NW, image=img)
        canvas.bind("<Button-1>", self.select)
        canvas.bind("<Button-2>", self.next)
        canvas.bind("<Button-3>", sys.exit)
        # Used to determine continue filename and dedup.
        self.selected_filenames = []


    def next(self, event):
        """
        Skip to the next montage.
        """
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<Button-2>")
        self.root.destroy()


    def select(self, event):
        """
        Select an image and skip to the next montage.
        """
        # Locate the image that matches this point.
        point = Point(event.x, event.y)
        for p in self.rect_points:
            if point.within_rect(p['point_ul'], p['point_lr']):
                selected_filename = p['filename']
                print('%s' % (selected_filename,))
                break
        else:
            # Outside all images.
            return
        new_filename = False
        if len(self.selected_filenames) > 0:
            bigger_file = selected_filename > self.selected_filenames[-1]
        else:
            bigger_file = True
        if selected_filename not in self.selected_filenames:
            self.selected_filenames.append(selected_filename)
            self.selected_filenames.sort()
            new_filename = True
            print('Adding %s' % (selected_filename,))
        # EIther first file or a filename that is after the current max.
        if bigger_file:
            # Have a new file to continue with.
            with open(self.continue_filename, 'w') as c:
                c.write('%s\n' % (selected_filename,))
            print('Wrote %s to %s' % (selected_filename, self.continue_filename))
        if new_filename:
            # dedup
            with open(self.out_filename, 'a') as out_file:
                out_file.write('%s\n' % (selected_filename,))
            print('Wrote %s to %s' % (selected_filename, self.out_filename))


class Point():
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __str__(self):
        return "Point(%3.2f,%3.2f)" % (self.x, self.y) 

    def within_rect(self, point_ul, point_lr):
        """
        Return True if this point is within a rectangle defined by
        point_ul (upper left) and point_lr (lower right).
        """
        if self.x < point_ul.x or self.y < point_ul.y:
            # To the left or above the rectangle
            return False
        if self.x > point_lr.x or self.y > point_lr.y:
            # Below or to the right of the rectangle
            return False
        return True


def calc_rect_points(args):
    """
    Calculate the position of the upper left and lower right points
    in each image.
    """
    points = []
    for i in range(args.n_rows * args.row_size):
        row = int(i / args.row_size)
        col = int(i % args.row_size)
        point_ul = Point( 11 + 220 * col, 11  + 242 * row)
        point_lr = Point(212 + 220 * col, 230 + 242 * row)
        # Dropped the .3 from the LR X component because
        # .3 * 5 = 1.5 pixels which is a small error.
        points.append(dict(i=i, row=row, col=col,
                           point_ul=point_ul, point_lr=point_lr))
    return points


def main(args):
    in_filenames  = [file for file in os.listdir(args.in_dir)
                     if file[-3:] in ['gif', 'png', 'jpg', 'lnk']]
    n_file = 0
    n_images = args.n_rows * args.row_size
    part = 1                    # Section of files to skip over
    try:
        with open(args.continue_filename) as c:
            start_filename = c.readline().strip().split('/')[1]
    except FileNotFoundError:
        start_filename = ''
        print('Skipping to just after %s' % (start_filename,))
    batch_filenames = []
    for in_filename in in_filenames:
        n_file += 1
        if start_filename and part == 1 and not in_filename.startswith(start_filename):
            continue
        else:
            if part == 1:
                # Skip just after this filename
                part = 2
                continue
            part = 2
        in_filename_path = os.path.join(args.in_dir, in_filename)
        if in_filename_path.endswith('.lnk'):
            # Get the base name of the file with its image extension.
            in_ext = ' - Shortcut.lnk'
            if in_filename.endswith(in_ext):
                in_filename = in_filename[:-len(in_ext)]
            # The files being linked to are in this directory.
            in_filename_path = os.path.join(args.alt_in_dir, in_filename)
            for ext in ['gif', 'png', 'jpg']:
                in_filename_path = in_filename_path[:-3] + ext
                if os.path.exists(in_filename_path):
                    break
            else:
                print('Unable to find this file: %s' % in_filename_path)
                exit(1)
        batch_filenames.append(in_filename_path)
        if len(batch_filenames) < n_images:
            continue
        
        root = tk.Tk()
        montage_filename_path = os.path.join(args.tmp_dir, 'montage.png')
        cmd = ['magick', 'montage', '-label', '%[basename]\n%[width]x%[height]',
               '-size', '1000x1000', '-auto-orient',
               '-geometry',
               '%sx%s+5+5' % (args.thumb_size, args.thumb_size),
               '-tile', '%sx' % (args.row_size,),
               '-frame', '5',
               '-shadow']
        cmd += batch_filenames
        cmd.append(montage_filename_path)
        ret = subprocess.call(cmd)
        if ret != 0:
            raise Exception('Got a subprocess.call error %s, command=%s' % (ret,' '.join(cmd)))
        (image_width, image_height) = get_image_size(montage_filename_path)

        canvas = tk.Canvas(root, width =image_width, height = image_height)
        canvas.pack()

        rect_points = calc_rect_points(args)
        for p in rect_points:
            p['filename'] = batch_filenames[p['i']]

        # Putting the next line into __init__ causes the image to not appear.
        img = tk.PhotoImage(master=canvas, file=montage_filename_path)
        application = Application(args, root, canvas,
                                  os.path.join(args.in_dir, in_filename),
                                  montage_filename_path, img,
                                  rect_points)
        #application = Application(root, canvas, montage_filename_path, tk.PhotoImage(file=montage_filename_path))
        batch_filenames = []
        tk.mainloop()
        os.remove(montage_filename_path)


if __name__ == '__main__':
    main(build_parser().parse_args())
