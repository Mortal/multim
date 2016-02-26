#!/usr/bin/python
"""
multiconvert.py -- run convert(1) on multiple files in a directory.
The script accepts the same parameters as convert(1), except the input-file
and output-file must name existing directories instead of files.
The script accepts an additional parameter -jn, where n is the parallellism,
which is passed on to make(1) to run convert(1) in parallel.

For example, the following command will resize images in the directory
`Pictures` by 50%, storing the result in `Resized`, resizing up to
four images at a time:
    multiconvert.py -j4 Pictures -resize 50% Resized

Mathias Rav, November 2013
"""

import os
import re
import stat
import subprocess
import sys


NO_ARG = """
-adjoin -antialias -append -auto-gamma -auto-level -auto-orient
-black-point-compensation -clamp -clip -clip -clut -coalesce -combine -compare
-composite -contrast -deconstruct -despeckle -enhance -equalize -fft -flatten
-flatten -flip -flop -hald-clut -help -identify -ift -magnify -matte -monitor
-monochrome -mosaic -negate -normalize -ping -quiet -regard-warnings -render
-respect-parentheses -reverse -separate -strip -synchronize -taint -transform
-transpose -transverse -trim -unique-colors -verbose -version -view
""".split()


SINGLE_ARG = """
-adaptive-blur -adaptive-resize -adaptive-sharpen -affine -alpha -annotate
-attenuate -authenticate -background -bench -bias -black-threshold
-blue-primary -blue-shift -blur -border -bordercolor -brightness-contrast
-caption -cdl -channel -charcoal -chop -clip-mask -clip-mask -clip-path
-clip-path -clone -color-matrix -colorize -colors -colorspace -comment -complex
-compose -compress -contrast-stretch -convolve -crop -cycle -debug -decipher
-define -delay -delete -density -depth -deskew -direction -display -dispose
-distort -distribute-cache -dither -draw -duplicate -edge -emboss -encipher
-encoding -endian -evaluate -evaluate-sequence -extent -extract -family
-features -fill -filter -floodfill -font -format -frame -function -fuzz -fx
-gamma -gaussian-blur -geometry -gravity -grayscale -green-primary -implode
-insert -intensity -intent -interlace -interline-spacing -interpolate
-interpolative-resize -interword-spacing -kerning -label -lat -layers -level
-level-colors -limit -linear-stretch -liquid-rescale -list -log -loop -mask
-mattecolor -median -metric -mode -modulate -morph -morphology -motion-blur
-noise -opaque -ordered-dither -orient -page -paint -perceptible -pointsize
-polaroid -poly -posterize -precision -preview -print -process -profile
-quality -quantize -radial-blur -raise -random-threshold -red-primary -region
-remap -repage -resample -resize -roll -rotate -sample -sampling-factor -scale
-scene -seed -segment -selective-blur -sepia-tone -set -shade -shadow -sharpen
-shave -shear -sigmoidal-contrast -size -sketch -smush -solarize -sparse-color
-splice -spread -statistic -stretch -stroke -strokewidth -style -support -swap
-swirl -texture -threshold -thumbnail -tile -tile-offset -tint -transparent
-transparent-color -treedepth -type -undercolor -units -unsharp -vignette
-virtual-pixel -wave -weight -white-point -white-threshold -write
""".split()


def main():
    skip_next = False
    args = list(sys.argv[1:])
    inputs_seen = 0
    parallel = '-j1'
    input_dir = None
    output_dir = None

    for i in range(len(args)):
        arg = args[i]
        if skip_next:
            skip_next = False
            continue
        if arg in SINGLE_ARG:
            skip_next = True
            continue
        if arg in NO_ARG:
            continue
        if re.match(r'-j[0-9]*', arg):
            parallel = arg
            args[i] = ''
            continue
        try:
            st = os.stat(arg)
        except FileNotFoundError:
            continue

        if stat.S_ISDIR(st.st_mode):
            if inputs_seen == 0:
                # Input
                input_dir = arg
                args[i] = '$<'
            elif inputs_seen == 1:
                # Output
                output_dir = arg
                args[i] = '$@'
            else:
                print("Too many directories in command line")

            inputs_seen += 1

    filenames = [
        f for f in os.listdir(input_dir)
        if re.match(r'[^ ]*\.[^ ]*', f)]
    make_command = ['make', '-f', '-', parallel]
    convert_command = ['convert'] + args
    input_dir_relative_to_output_dir = os.path.relpath(input_dir, start=output_dir)

    makefile = ('INPUTS := %s\nall: $(INPUTS)\n$(INPUTS):%%: %s/%%\n\t%s' %
                (' '.join(filenames),
                 input_dir_relative_to_output_dir,
                 ' '.join(convert_command)))

    returncode = subprocess.call(
        make_command, stdin=makefile.encode('utf8'), cwd=output_dir)
    if returncode:
        raise SystemExit(returncode)


if __name__ == "__main__":
    main()
