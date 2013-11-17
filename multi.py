#!/usr/bin/python

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
