"""
Read the header for a .png image file.

Usage:
  import png
  img = Png('filename.png')

  # Prints an empty dict or a dict with these keys:
  #   width, height, bit_depth, color_type,
  #   compression_method, interlace_method, filter_method
  print(img.get_header()
"""

class Png():
    ck_type_header = b'IHDR'

    def __init__(self, image_filename):
        self.file = open(image_filename, 'rb')

    def close(self):
        self.file.close()

    def is_png_header(self):
        bytes = self.file.read(8)
        for (e_byte, byte) in zip([b'\x89', b'P', b'N', b'G', b'\r', b'\n', b'\x1a', b'\n'], bytes):
            if ord(e_byte) != byte:
                print('Got an unexpected byte reading the PNG header', ord(e_byte), byte)
                return False
            return True

    def b_to_int(self, bytes):
        return ((bytes[0] * 256 + bytes[1]) * 256 + bytes[2]) * 256 + bytes[3]

    def read_chunk_header(self,bytes):
        return (self.b_to_int(bytes[0:4]), bytes[4:])

    def read_header(self, length):
        bytes = self.file.read(length)
        width = self.b_to_int(bytes[:4])
        height = self.b_to_int(bytes[4:8])
        (bit_depth, color_type, compression_method, interlace_method, filter_method) = bytes[8:]
        return (width, height, bit_depth, color_type, compression_method, interlace_method, filter_method)

    """file format:
 width (4 bytes),
 height (4 bytes),
 bit depth (1 byte),
 color type (1 byte),
 compression method (1 byte),
 filter method (1 byte),
 interlace method (1 byte) """

    def get_header(self):
        """
        Return a dict with the attributes of the PNG header chunk. It is the first chunk.
        On failure, either an exception or an empty dict.
        """
        if self.is_png_header():
            (length, ck_type) = self.read_chunk_header(self.file.read(8))
            if ck_type == self.ck_type_header:
                (width, height, bit_depth, color_type,
                 compression_method, interlace_method, filter_method) = self.read_header(length)
                return dict(zip(
                    ['width', 'height', 'bit_depth', 'color_type',
                     'compression_method', 'interlace_method', 'filter_method'],
                    [width, height, bit_depth, color_type,
                     compression_method, interlace_method, filter_method]))
        return dict()
