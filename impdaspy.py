#!/usr/bin/env python
# _*_ coding: utf-8 _*_

from numpy import fromfile
import sys
import matplotlib.pyplot as plt

"""
    Open a binary file written by DAS (LabView) and save it to a text file.

"""
plt.switch_backend('qt4Agg')
plt.ion()

fid = open(sys.argv[1], 'rb')
dim = fromfile(fid, dtype='>u4', count=2)
temp = fromfile(fid, dtype='>f',count=dim[0] * dim[1]).reshape(dim[1],
                dim[0], order='F').T # Change to column reshape format (Fortran)

nchannels = temp[0, 1]
fs = temp[0, 0]
dim = fromfile(fid, dtype='>u4', count=1)
Name = []

for k in xrange(dim):
    Name.append(fromfile(fid,dtype='B',count=fromfile(fid, dtype='>u4',
                                                      count=1)))

hour = fromfile(fid, dtype='B', count=fromfile(fid, dtype='>u4', count=1))
signal = fromfile(fid, dtype='>f')
signal = signal.reshape(dim, len(signal) / float(dim), order='F')
plt.plot(signal[0])
