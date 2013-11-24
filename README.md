By Mathias Rav in November 2013.

`multi.py`
==========

Run a command on multiple files in a directory.

The script treats the argument list as a command line to run.

The first argument that matches the regex -j[0-9]* is removed from the
argument list and treated as a GNU make parameter instead.

The first argument that names an existing directory is replaced by the list
of files in that directory, and is run with make.

For example, the following command will rotate images in the directory
`Pictures` according to their Exif orientation tag, processing up to
four files at a time:

    multi.py -j4 jhead -autorot Pictures

`multiconvert.py`
=================

`multiconvert.py` -- run convert(1) on multiple files in a directory.

The script accepts the same parameters as convert(1), except the input-file
and output-file must name existing directories instead of files.

The script accepts an additional parameter -jn, where n is the parallellism,
which is passed on to make(1) to run convert(1) in parallel.

For example, the following command will resize images in the directory
`Pictures` by 50%, storing the result in `Resized`, resizing up to
four images at a time:

    multiconvert.py -j4 Pictures -resize 50% Resized
