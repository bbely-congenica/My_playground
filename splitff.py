#!/usr/bin/env python

from __future__ import print_function
from builtins import zip
from builtins import map
from builtins import range
import argparse
import os
from mmap import mmap
from readchunk import Chunk

parser = argparse.ArgumentParser()
parser.add_argument('-f', dest='filename', help="name of file to split", required=True)
parser.add_argument('-s', dest='separator', help="separator", required=False, default='//')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-fileno', dest='filenumber', type=int, help="number of subfiles to create")
group.add_argument('-entryno', dest='entrynumber', type=int, help="number of entries per subfile")
parser.add_argument('-p', dest='prefix', help="subfile prefix", default=None)
args = parser.parse_args()

filename_base, filename, = os.path.split(args.filename)
stem, ext, = os.path.splitext(filename)

args.separator = b'%s\n' % args.separator.encode()

if not args.prefix:
    args.prefix = stem

if args.entrynumber:
    filenum = 1
    entrynum = 0
    fname = '%s_%d%s' % (args.prefix, filenum, ext)
    outfile = open(fname, 'w')
    with open(filename, 'r+b') as f:
        for l in f:
            print(l, file=outfile, end='')
            if l.endswith(args.separator):
                entrynum += 1
                if entrynum % args.entrynumber == 0:
                    outfile.close()
                    filenum += 1
                    outfile = open('%s_%d%s' % (args.prefix, filenum, ext), 'w')
    if filenum == 1:
        print('Less entries (%s) than split (%s): doing nothing' % (entrynum, args.entrynumber))
        os.remove(fname)
else:
    f = open(args.filename, 'r+b')
    m = mmap(f.fileno(), 0)
    s = len(m)  # size in bytes
    l = [m.find(args.separator, x) + len(args.separator) for x in [x * s // args.filenumber for x in range(1, args.filenumber)]]  # list of positions for separator
   # cannot comment this, too sky hight
    for ((s, e,), outfile) in zip(list(map(lambda x, y: (x, y), [0] + l, l + [s])), [open('%s_%d%s' % (args.prefix, filenum, ext), 'w') for filenum in range(1, args.filenumber + 1)]):
        print(Chunk(args.filename, s, e), file=outfile, end='')
        outfile.close()
