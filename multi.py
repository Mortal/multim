#!/usr/bin/python

## Author: Mathias Rav
## Date: November 2013

## multi.py -- run a command on multiple files in a directory.
## The script treats the argument list as a command line to run.
## The first argument that matches the regex -j[0-9]* is removed from the
## argument list and treated as a GNU make parameter instead.
## The first argument that names an existing directory is replaced by the list
## of files in that directory, and is run with make.

## For example, the following command will rotate images in the directory
## `Pictures` according to their Exif orientation tag, processing up to
## four files at a time:
##     multi.py -j4 jhead -autorot Pictures

import os
import re
import stat
import subprocess
import sys

args = list(sys.argv[1:])
parallel = '-j1'
target_dir = None

for i in range(len(args)):
    arg = args[i]
    if re.match(r'-j[0-9]*', arg):
        parallel = arg
        args[i] = ''
        continue
    try:
        st = os.stat(arg)
    except FileNotFoundError:
        continue

    if stat.S_ISDIR(st.st_mode):
        if target_dir is None:
            target_dir = arg
            args[i] = '$@'
        else:
            print("Too many directories in command line")

filenames = (f for f in os.listdir(target_dir) if re.match(r'[^ ]*\.[^ ]*', f))
make_command = ['make', '-B', '-f', '-', parallel]

makefile = 'TARGETS := '+(' '.join(filenames))+'\nall: $(TARGETS)\n$(TARGETS):%:\n\t'+(' '.join(args))

with subprocess.Popen(make_command, stdin=subprocess.PIPE, cwd=target_dir) as proc:
    proc.communicate(makefile.encode('utf8'))
    proc.wait()