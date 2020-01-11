"""
Get the size of an image.
"""


import argparse
import struct
import imghdr
import subprocess


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__.strip())

    parser.add_argument('image_filename',
                        help='Input image filename.')
    return parser


def get_image_size(fname):
    """
    magick has a way to determine the dimensions of an image.
    it works for many image types.
    returns: [width, height]

    If an error is encountered, [0,0] is returned
    """
    cmd = ['magick', 'identify', '-format', '(%w,%h)', '-ping', fname]
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.returncode == 0:
        return eval(process.stdout)
    print(process.stderr.decode("utf-8"))
    return [0,0]


def get_image_size_old(fname):
    """
    Determine the image type of fname and return its size.
    On error returns None
    """
    with open(fname, 'rb') as fhandle:
        head = fhandle.read(24)
        if len(head) != 24:
            raise Exception('Bad header length %s, file=%s' % (len(head), fname))
        if imghdr.what(fname) == 'png':
            check = struct.unpack('>i', head[4:8])[0]
            if check != 0x0d0a1a0a:
                raise Exception('Bad check %s, file=%s' % (check, fname))
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
                raise Exception('unknwn error, file=%s' % (fname,))
        else:
            raise Exception('unknown file type %s, file=%s' % (imghdr.what(fname), fname))
        return width, height


def main(args):
    (width, height) = get_image_size(args.image_filename)
    print('width', width, ', height', height)


if __name__ == '__main__':
    main(build_parser().parse_args())
