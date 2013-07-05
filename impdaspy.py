#!/usr/bin/env python
# _*_ coding: utf-8 _*_

"""
    Open a binary file written by DAS (LabView) and save it to a text file.

"""
from numpy import fromfile
import sys
import matplotlib.pyplot as plt

def bin2py(filename):

    """
        Funtion to open a binary file written by Data acquisition system.
    """

    fid = open(filename, 'rb')
    dim = fromfile(fid, dtype='>u4', count=2)
    temp = fromfile(fid, dtype='>f', count=dim[0] * dim[1]).reshape(dim[1],
                                                                    dim[0],
                                                                    order='F').T

    nchannels = temp[0, 1]
    fs_c = temp[0, 0]
    dim1 = fromfile(fid, dtype='>u4', count=1)
    name = []
    name_c = []

    for iter1 in xrange(dim1):

        name.append(fromfile(fid, dtype='B', count=fromfile(fid, dtype='>u4',
                                                            count=1)))
        name_c.append(' '.join([chr(str_it) for str_it in name[iter1]]))



    hour = fromfile(fid, dtype='B', count=fromfile(fid, dtype='>u4', count=1))
    hour = ' '.join([chr(str_it2) for str_it2 in hour])
    signal = fromfile(fid, dtype='>f')
    signal = signal.reshape(dim1, len(signal) / float(dim1), order='F')
    allsig = []

    for iter2 in xrange(dim1):
        allsig.append(signal[iter2])

    return allsig, fs_c, nchannels, name_c, hour


if __name__ == '__main__':

    DATA, FS, NC, NAMES, HOUR = bin2py(sys.argv[1])
    print "Number of channels: %d\nSampling frequency> %.2f Hz\nData were colected at: %s\nThe Name of signals are: %s and %s" % (NC, FS, HOUR, NAMES[0], NAMES[1])
    plt.plot(DATA[0])
    plt.show()
