#!/usr/bin/env python

"""
Display a png file and report the mouse position on a mouse click.
"""

#from tkinter import *      
import tkinter as tk

margin_x = 20
margin_y = 20

ck_type_header = b'IHDR'

class Application():
    def __init__(self, root, canvas, img, png_header, xy):
        """
        xy is an empty list object used to return with width and height.
        """
        self.root = root
        self.png_header = png_header
        self.xy = xy
        canvas.create_image(margin_x, margin_y, anchor=tk.NW, image=img)      
        canvas.bind("<Button-1>", self.callback)


    def callback(self, event):  
        x = event.x - margin_x
        y = event.y - margin_y
        if (x >= 0 and y >= 0
            and x < self.png_header['width']
            and y < self.png_header['height']):
            # Return the (x,y) position to the caller.
            self.xy.append(x)
            self.xy.append(y)
            self.root.destroy()


def is_png_header(file):
    bytes = file.read(8)
    for (e_byte, byte) in zip([b'\x89', b'P', b'N', b'G', b'\r', b'\n', b'\x1a', b'\n'], bytes):
        if ord(e_byte) != byte:
            print('Got an unexpected byte reading the PNG header', ord(e_byte), byte)
            return False
        return True

def b_to_int(bytes):
    return ((bytes[0] * 256 + bytes[1]) * 256 + bytes[2]) * 256 + bytes[3]

def read_chunk_header(bytes):
    return (b_to_int(bytes[0:4]), bytes[4:])

def read_header(file, length):
    bytes = file.read(length)
    width = b_to_int(bytes[:4])
    height = b_to_int(bytes[4:8])
    (bit_depth, color_type, compression_method, interlace_method, filter_method) = bytes[8:]
    return (width, height, bit_depth, color_type, compression_method, interlace_method, filter_method)


"""image's width (4 bytes), height (4 bytes), bit depth (1 byte), color type (1 byte), compression method (1 byte), filter method (1 byte), and interlace method (1 byte) """

def get_png_header(filename):
    """
    Return a dict with the attributes of the PNG header chunk. It is the first chunk.
    On failure, either an exception or an empty dict.
    """
    with open(filename, 'rb') as file:
        if is_png_header(file):
            (length, ck_type) = read_chunk_header(file.read(8))
            if ck_type == ck_type_header:
                (width, height, bit_depth, color_type, compression_method, interlace_method, filter_method) = read_header(file, length)
                return dict(zip([
                    'width', 'height', 'bit_depth', 'color_type', 'compression_method', 'interlace_method', 'filter_method'],[width, height, bit_depth, color_type, compression_method, interlace_method, filter_method]))
    return dict()


def main():
    filename = "ball.png"
    png_header = get_png_header(filename)

    root = tk.Tk()      
    canvas = tk.Canvas(root, width = png_header['width'] + margin_x * 2,
                       height = png_header['height'] + margin_y * 2)
    canvas.pack()      
    # Putting the next line into __init__ causes the image to not appear.
    img = tk.PhotoImage(file=filename)
    xy = []
    application = Application(root, canvas, img, png_header, xy)
    tk.mainloop()
    (x, y) = xy
    print(x, y)

if __name__ == '__main__':
    main()
