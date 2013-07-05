"""
    Module to convert the codes from Mecanica software, written in Matlab
    to the free world of Python
"""

import numpy as np


def impdaspy(filename, savef=False):

    """
        Open a binary file written by Data Acquisition System (DAS).

        Parameters:
        ----------
        filename : file or str
               Open file object or filename
        savef : boolean, optional
            If true, saves the binary file to a text file

       Returns:
       -------
       all_sign : array_like
            All signals acquired with DAS. The number of signal returned
            is equal to the number of channels used in the acquisition.
       config : dict
           Some configuration parameters: sampling frequency, file names,
           acquisition hour, positivegain, negative gain
    """

    fid = open(filename, 'rb')
    dim = np.fromfile(fid, dtype='>u4', count=2)
    temp = np.fromfile(fid, dtype='>f', count=dim[0] * dim[1]).reshape(dim[1],
                                                                       dim[0],
                                                                       order=
                                                                       'F').T
    freq = temp[0, 0]
    nchannels = temp[0, 1]
    #dgpoli = dim[1]
    temp = temp[1::, :]

    baseline = temp[0:nchannels, 0]
    #basenoise = temp[0:nchannels, 1]
    temp = temp[nchannels + 1::, :]

    positivegain = np.concatenate((np.fliplr(temp[0:nchannels, :]),
                                   np.zeros((nchannels, 1))), axis=0)
    temp = temp[nchannels + 1::, :]
    negativegain = np.concatenate((np.fliplr(temp[0:nchannels, :]),
                                   np.zeros((nchannels, 1))), axis=0)

    dim1 = np.fromfile(fid, dytpe='>u4', count=1)
    name = []
    name_c = []

    for iter1 in xrange(dim1):
        name.append(np.fromfile(fid, dtype='B', count=np.fromfile(fid,
                                                                  dtype='>u4',
                                                                  count=1)))
        name_c.append(' '.join([chr(str_it1) for str_it1 in name[iter1]]))

    hour = np.fromfile(fid, dtype='B', count=np.fromfile(fid, dtype='>u4',
                                                         count=1))
    hour = ' '.join([chr(str_it2) for str_it2 in hour])
    signal = np.fromfile(fid, dtype='>f')
    signal.reshape(dim1, len(signal) / float(dim1), order='F')
    all_sig = [signal[iter2] for iter2 in dim1]

    #remove baseline

    all_sig = [all_sig[iter3] - baseline[iter3] for iter3 in dim1]

    config = {'fs': freq, 'hour': hour, 'names': name_c,
              'posgain': positivegain, 'neggain': negativegain}

    return all_sig, config
