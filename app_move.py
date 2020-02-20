#!/usr/bin/env python

"""
Display an image file and look at which mouse button was clicked.
Left - skip to the next image
Middle - output the name of the file, and skip to the next image
Right - stop
"""
#
r"""
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
                        default='00SPREAD',
                        help='Input directory. Default: %(default)s.')
    parser.add_argument('-o', '--out_filename',
                        default='spread-images.txt',
                        help='Output filename for the filenames. Default: %(default)s.')
    parser.add_argument('-t', '--tmp_dir',
                        default='TMP',
                        help='Temp directory. Default: %(default)s.')
    parser.add_argument('-s', '--start_filename',
                        default='000113a-8.jpg',
                        help='Filename to start with. Default: %(default)s.')
    return parser


class Application():
    def __init__(self, root, canvas, source_image_filename, in_image_filename, img, scale_factor, out_filename):
        self.root = root
        self.canvas = canvas
        self.source_image_filename = source_image_filename
        self.in_image_filename = in_image_filename
        self.scale_factor = scale_factor
        self.out_filename = out_filename
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
        with open(self.out_filename, 'a') as out_file:
            out_file.write('%s\n' % (self.source_image_filename,))
        x = round(event.x / (int(self.scale_factor)/100))
        y = round(event.y / (int(self.scale_factor)/100))
        if x >= 0 and y >= 0:
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<Button-2>")
            self.root.destroy()


def add_to_clipboard(text):
    """
    Put the text in the clipboard, removing whitespace from either end. What actually
    happens is that an extra character is appended to the clipboard which needs to be
    deleted to get the text.
    """
    command = 'echo "' + text.strip() + '"| /cygdrive/c/Windows/System32/clip.exe'
    os.system(command)


def main(args):
    in_filenames  = [file for file in os.listdir(args.in_dir)
                     if file[-3:] in ['gif', 'png', 'jpg']]
    n_file = 0
    part = 1                    # Section of files to skiip over
    for in_filename in in_filenames:
        n_file += 1
        if part == 1 and not in_filename.startswith(args.start_filename):
            continue
        else:
            part = 2
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

        img = tk.PhotoImage(master=canvas, file=png_filename_path)
        application = Application(root, canvas, os.path.join(args.in_dir, in_filename),
                                  png_filename_path, img, scale_factor, args.out_filename)
        #application = Application(root, canvas, png_filename_path, tk.PhotoImage(file=png_filename_path))
        tk.mainloop()
        add_to_clipboard(in_filename)
        os.remove(png_filename_path)
        time.sleep(1)


if __name__ == '__main__':
    main(build_parser().parse_args())
