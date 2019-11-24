#!/usr/bin/env python

"""
Remove duplicates.

Calculates md5 for each file that doesn't have an .md5 file.

The .md5 file contains the md5 value followed by a blank with the rest
of the line being the filename. The .md5 files are sorted and
duplicates identified.
"""

import argparse
from datetime import datetime
import glob
import hashlib
import imghdr
import os
import os.path
import struct
import subprocess

def build_parser():
    parser = argparse.ArgumentParser(description=__doc__.strip())

    parser.add_argument('-d', '--dir',
                        default='00SPREAD',
                        help='Output directory. Default: %(default)s.')
    parser.add_argument('-n', '--noop', action='store_true',
                        default=False,
                        help = 'compute the md5 but do not write the file'
                        '. Default: %(default)s.')
    parser.add_argument('-f', '--n_files', type=int,
                        default=10000000,
                        help='Number of files to process'
                        '. Default: %(default)s.')

    return parser



# Doing the md5 calculation this way because the python way
# gets into character set problems with binary files.
def compute_md5(filename):
    """
    Compute the md5 value for the contents of a file.
    """
    result = subprocess.run(['md5sum.exe', filename], stdout=subprocess.PIPE)
    r = result.stdout
    md5 = r[:32].decode("utf-8") 
    return md5


def file_date(filename):
    """
    Get a datetime object from a file's ctime.
    """
    return  datetime.fromtimestamp(os.path.getctime(filename))


def get_image_size(fname):
    """
    Determine the image type of fname and return its size.
    Returns 0, 0 if an error is detected.
    Sometime this fails and returns a height of 1.
    """
    with open(fname, 'rb') as fhandle:
        head = fhandle.read(24)
        if len(head) != 24:
            return 0, 0
        if imghdr.what(fname) == 'png':
            check = struct.unpack('>i', head[4:8])[0]
            if check != 0x0d0a1a0a:
                return 0, 0
            width, height = struct.unpack('>ii', head[16:24])
        elif imghdr.what(fname) == 'gif':
            width, height = struct.unpack('<HH', head[6:10])
        elif imghdr.what(fname) == 'jpeg':
            try:
                fhandle.seek(0) # Read 0xff next
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xff:
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', fhandle.read(2))[0] - 2
                # We are at a SOFn block
                fhandle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack('>HH', fhandle.read(4))
            except Exception: #IGNORE:W0703
                return 0, 0
        else:
            return 0, 0
        return width, height


def file_wxh(filename):
    """
    Use the 'file' command to determie the file width and height.
    """
    # Output looks like this:
    #   filename JPEG image data, baseline, precision 8, 1000x1333, frames 3
    # Grab the width x height near the end and return integers.
    command = 'file "' + filename + '"'
    result = subprocess.check_output(command, shell=True)
    return [int(x) for x in result.decode("utf-8").split(',')[-2].strip().split('x')]


def image_size(filename):
    (w, h) = get_image_size(filename)
    if w == 0 or h == 1:
        (w, h) = file_wxh(filename)
    return (w, h)


def main(args):
    filenames = []
    for file_ext in ['*.jpg', '*.gif', '*.png']:
        filenames = filenames + glob.glob(os.path.join(args.dir, file_ext))
    
    file_count = 0
    md5_dict = dict()
    for filename in filenames:
        if file_count > args.n_files:
            break
        file_count += 1
        md5_filename = filename[:-3] + 'md5'
        md5_exists = os.path.isfile(md5_filename)
        if not md5_exists:
            md5 = compute_md5(filename)
            with open(md5_filename, 'w') as md5_file:
                md5_file.write('%s\n' % (md5,))
        else:
            with open(md5_filename) as md5_file:
                md5 = md5_file.readline().strip()
        if md5 in md5_dict:
            md5_dict[md5].append(filename)
        else:
            md5_dict[md5] = [ filename ]
    center_dir = '%s-CENTER' % (args.dir,)
    n_errors = 0
    for md5 in sorted(md5_dict.keys()):
        if len(md5_dict[md5]) > 1:
            center_exists = []
            filename_dates = []
            filenames = sorted(md5_dict[md5])
            oldest_date = datetime.now()
            oldest_filename = None
            for filename in filenames:
                center_filename = filename.replace(args.dir, center_dir)
                center_exists.append(os.path.isfile(center_filename))
                filename_date = file_date(filename)
                if filename_date < oldest_date:
                    oldest_date = filename_date
                    oldest_filename = filename
                filename_dates.append(filename_date)
            if oldest_filename:
                if any(center_exists):
                    # At least one is in center_dir
                    print('Too many in center_dir for', filenames)
                    print(center_exists)
                    print(md5, oldest_filename)
                    print('-------------------------------------------------------------')
                    n_errors += 1
                else:
                    if args.noop:
                        print(filenames)
                        print('keeping', oldest_filename)
                        print(filename_dates)
                    for filename in filenames:
                        if filename != oldest_filename:
                            if args.noop:
                                print('rm', filename)
                            else:
                                os.remove(filename)
            else:
                print('Unable to determine oldest filename', filenames)
                print('-------------------------------------------------------------')
                n_errors += 1

    if n_errors:
        print('n_errors=%s' % (n_errors,))

if __name__ == '__main__':
    main(build_parser().parse_args())
