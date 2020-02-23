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
Map mouse coordinates to an image file.
This file can be written to out_filename.

Add logic for the mouse callbacks as noted above.

Change the logic for continue_filename. Move it out
of callbacks and put it into the main loop. It is the
last file in a batch.

done:
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

    parser.add_argument('-o', '--out_filename',
                        default='spread-images.txt',
                        help='Output filename for the filenames that were selected. '
                        'Default: %(default)s.')

    parser.add_argument('-n', '--n_images', type=int,
                        default=15,
                        help='Number of images in a montage. '
                        'Default: %(default)s.')

    parser.add_argument('-t', '--tmp_dir',
                        default='tests/tmp',
                        help='Temp directory. Default: %(default)s.')
#                        default='TMP',

    parser.add_argument('-c', '--continue_filename',
                        default='spread-continue.txt',
                        help='Filename that contains the last file processed. '
                        'Default: %(default)s.')
    return parser


class Application():
    def __init__(self, root, canvas, source_image_filename, in_image_filename, img, scale_factor, out_filename, continue_filename):
        self.root = root
        self.canvas = canvas
        self.source_image_filename = source_image_filename
        self.in_image_filename = in_image_filename
        self.scale_factor = scale_factor
        self.out_filename = out_filename
        self.continue_filename = continue_filename
        (self.image_width, self.image_height) = get_image_size(in_image_filename)
        (self.source_image_width, self.source_image_height) = get_image_size(source_image_filename)

        canvas.create_image(0, 0, anchor=tk.NW, image=img)
        canvas.bind("<Button-1>", self.next)
        canvas.bind("<Button-2>", self.record)
        canvas.bind("<Button-3>", sys.exit)


    def next(self, event):
        """
        Skip to the next image.
        """
        with open(self.continue_filename, 'w') as c:
            c.write('%s\n' % (self.source_image_filename,))
        x = round(event.x / (int(self.scale_factor)/100))
        y = round(event.y / (int(self.scale_factor)/100))
        if x >= 0 and y >= 0:
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<Button-2>")
            self.root.destroy()


    def record(self, event):
        """
        Record the filename ansd skip to the next image.
        """
        with open(self.continue_filename, 'w') as c:
            c.write('%s\n' % (self.source_image_filename,))
        with open(self.out_filename, 'a') as out_file:
            out_file.write('%s\n' % (self.source_image_filename,))
        x = round(event.x / (int(self.scale_factor)/100))
        y = round(event.y / (int(self.scale_factor)/100))
        if x >= 0 and y >= 0:
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<Button-2>")
            self.root.destroy()


def main(args):
    in_filenames  = [file for file in os.listdir(args.in_dir)
                     if file[-3:] in ['gif', 'png', 'jpg', 'lnk']]
    n_file = 0
    part = 1                    # Section of files to skiip over
    try:
        with open(args.continue_filename) as c:
            start_filename = c.readline().strip().split('/')[1]
    except FileNotFoundError:
        start_filename = ''
        print('Skipping to %s' % (start_filename,))
    batch_filenames = []
    for in_filename in in_filenames:
        n_file += 1
        if start_filename and part == 1 and not in_filename.startswith(start_filename):
            continue
        else:
            part = 2
        in_filename_path = os.path.join(args.in_dir, in_filename)
        if in_filename_path.endswith('.lnk'):
            in_ext = ' - Shortcut.lnk'
            if in_filename.endswith(in_ext):
                in_filename = in_filename[:-len(in_ext)]
            # The .lnk files came from this directory
            in_filename_path = os.path.join(args.alt_in_dir, in_filename)
            for ext in ['gif', 'png', 'jpg']:
                in_filename_path = in_filename_path[:-3] + ext
                if os.path.exists(in_filename_path):
                    break
            else:
                print('Unable to find this file: %s' % in_filename_path)
                exit(1)
        batch_filenames.append(in_filename_path)
        if len(batch_filenames) < args.n_images:
            continue
        
        root = tk.Tk()
        montage_filename_path = os.path.join(args.tmp_dir, 'montage.png')
        cmd = ['magick', 'montage', '-label', '%[width]x%[height]',
               '-size', '1000x1000', '-auto-orient',
               '-geometry', '200x200+5+5', '-tile', '5x', '-frame', '5',
               '-shadow']
        cmd += batch_filenames
        batch_filenames = []
        cmd.append(montage_filename_path)
        for c in cmd:
            print(c)
        ret = subprocess.call(cmd)
        if ret != 0:
            raise Exception('Got a subprocess.call error %s, command=%s' % (ret,' '.join(cmd)))
        (image_width, image_height) = get_image_size(montage_filename_path)

        exit()
        canvas = tk.Canvas(root, width =image_width, height = image_height)
        canvas.pack()
        # Putting the next line into __init__ causes the image to not appear.

        img = tk.PhotoImage(master=canvas, file=montage_filename_path)
        application = Application(root, canvas, os.path.join(args.in_dir, in_filename),
                                  montage_filename_path, img, scale_factor, args.out_filename,
                                  args.continue_filename)
        #application = Application(root, canvas, montage_filename_path, tk.PhotoImage(file=montage_filename_path))
        tk.mainloop()
        os.remove(montage_filename_path)


if __name__ == '__main__':
    main(build_parser().parse_args())
