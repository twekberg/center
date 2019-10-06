====
TODO
====
Nothing.

======
Center
======

Displays an image from the input directory, adding vertical and
horizontal black space to center the point selected by the mouse.  The
resultant imaged is written to the output directory.
The right mouse button exits.

If the image is too large it is shrunk to fit within the screen.
If the image is smaller than the screen it is enlarged to just fit
within the screen.

Images already processed are skipped over in subsequent runs.

Usage::
   app.py [-h] [-i IN_DIR] [-o OUT_DIR] [-t TMP_DIR]

   Display a png file and report the mouse position on a mouse click.

   optional arguments:
     -h, --help            show this help message and exit
     -i IN_DIR, --in_dir IN_DIR
                           Input directory. Default: tests/in.
     -o OUT_DIR, --out_dir OUT_DIR
                           Output directory. Default: tests/out.
     -t TMP_DIR, --tmp_dir TMP_DIR
                           Temp directory. Default: tests/tmp.


cd ~/STUFF/N/O/SPELLSNO/IMAGES/BIG
~/src/center/app.py -i 00SPREAD -o 00SPREAD-CENTER -t TMP


Dependencies
~~~~~~~~~~~~

The programs here use the following tools:

ImageMagick - a powerful image manipulation tool. Handles many image
formats and is freely available.  The home page is
https://imagemagick.org/. The download page has detailed instructions
to install on a variety of operating systems. The programs here use
the convert program which comes with the installation. For windows, it should be
placed in this directory - /cygdrive/c/Windows/system32 - and your
PATH environment variable set to that directory.

MobaXterm - if you are running windows, you will need an X WIndow
System server. The author has been using MobaXterm for several years
and has found it to be very reliable. It can be found here: https://mobaxterm.mobatek.net/.

cygwin - a unix lookalike that runs on windows. It has the bash command
line and the cygwin terminal program to enter commands. It can be
found here: https://www.cygwin.com/.
The following
is a minimal list of the cygwin packages that are needed::

    Cygwin installation
    Python
      python37
      python37-imaging
      python37-imaging-tk
      python37-pip
      python37-setuptools
      python37-virtualenv
    Net
      openssh
      openssl

You may want to include additional packages.

Basic Installation
==================

Create a virtualenv::

  virtualenv-3.7 cen-env
  source cen-env/bin/activate

The author created a bash alias to make subsequent activates easier::

  alias acen='cd "$HOME/src/center/" ; source cen-env/bin/activate'

Running examples
================

Before running the examples::

    Start mobaxterm
    acen

