#!/usr/bin/env python

# _alive_in_production_

# *************************************************************
#
# $Source: /ebi/cvs/seqdb/sptrembl/src/python/tools/splitff.py,v $
# $Revision: 1.16 $
# $State: Exp $
# $Date: 2017/03/22 15:54:30 $
# $Author: awilter $
#
# $Log: splitff.py,v $
# Revision 1.16  2017/03/22 15:54:30  awilter
# Fix for python3
#
# Revision 1.15  2017/03/10 20:18:52  awilter
# Fixed for python 3
#
# Revision 1.14  2016/10/12 11:11:29  awilter
# Remove absolute_import module
#
# Revision 1.13  2016/06/29 22:53:26  awilter
# Typo
#
# Revision 1.12  2016/06/24 16:28:51  awilter
# Futurized
#
# Revision 1.10  2014/10/02 10:28:42  awilter
# xreadlines is deprecated
#
# Revision 1.9  2014/10/01 13:03:41  awilter
# Don't split if not needed
#
# Revision 1.8  2014/09/16 15:34:03  awilter
# PEP8
#
# Revision 1.7  2012/04/16 07:31:44  awilter
# format
#
# Revision 1.6  2011/09/14 16:09:57  pontikos
# *** empty log message ***
#
# Revision 1.5  2011/06/21 14:26:05  pontikos
# use Chunk instead of reading a whole section into memory
#
# Revision 1.4  2011/04/01 13:45:46  pontikos
# New python tools.
#
# Revision 1.3  2011/02/25 10:05:18  pontikos
# update to tools
#
#
#
# *************************************************************
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
    for ((s, e,), outfile) in zip(list(map(lambda x, y: (x, y), [0] + l, l + [s])), [open('%s_%d%s' % (args.prefix, filenum, ext), 'w') for filenum in range(1, args.filenumber + 1)]):
        print(Chunk(args.filename, s, e), file=outfile, end='')
        outfile.close()
