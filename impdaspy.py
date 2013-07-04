#!/usr/bin/env python
# _*_ coding: utf-8 _*_

from numpy import fromfile
import sys


fid = open(sys.argv[1], 'rb')
dim = fromfile(fid, dtype='>u4', count=2)
temp = fromfile(fid, dtype='>f',count=dim[0] * dim[1]).reshape(dim[0],
                                                                  dim[1], order='F').T # Change to column reshape format (Fortran)
nchannels = temp[0, 1]
fs = temp[0, 0]
temp = temp[1::, :]
baseline = temp[0:nchannels, 0]
temp = temp[nchannels::, :]
dim = fromfile(fid, dtype='>u4', count=1)
name = fromfile(fid, dtype='>u4') #tell  = 72
name1 = fromfile(fid, dtype='B', count=name) #tell = 77 dtype=B -> uchar
name = fromfile(fid, dtype='>u4') #tell  = 81
name1 = fromfile(fid, dtype='B', count=name) #tell = 88 dtype=B -> uchar
hora = fromfile(fid, dtype='>u4', count=1) #tell = 92
hora1 = fromfile(fid, dtype='B', count=hora) #tell = 100
signal = fromfile(fid, dtype='>f')
