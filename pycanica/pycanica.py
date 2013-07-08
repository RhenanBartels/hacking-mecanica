"""
    Module to convert the codes from Mecanica software, written in Matlab
    to the free world of Python
"""

import numpy as np
import sys
import Tkinter
import scipy.signal


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
    #handing error

    if not filename.endswith('bin'):
        raise Except("File must be have binary extension -> filename.bin")
    try:
        fid = open(filename, 'rb')
    except IOError:
        print "******* %s ---> File not found" % filename
        return None, None

    dim = np.fromfile(fid, dtype='>u4', count=2)
    temp = np.fromfile(fid, dtype='>f',
                       count=dim[0] * dim[1]).reshape(dim[1],
                                                      dim[0], order='F').T

    freq = temp[0, 0]
    nchannels = temp[0, 1]
    #dgpoli = dim[1]
    temp = temp[1::, :]

    baseline = temp[0:nchannels, 0]
    #basenoise = temp[0:nchannels, 1]
    temp = temp[nchannels::, :]

    positivegain = np.concatenate((np.fliplr(temp[0:nchannels, :]),
                                   np.zeros((nchannels, 1))), axis=1)
    temp = temp[nchannels::, :]
    negativegain = np.concatenate((np.fliplr(temp[0:nchannels, :]),
                                   np.zeros((nchannels, 1))), axis=1)

    dim1 = np.fromfile(fid, dtype='>u4', count=1)
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
    signal =  signal.reshape(dim1, len(signal) / float(dim1), order='F')

    #remove baseline

    all_sig = np.array([signal[iter3] - baseline[iter3]
                        for iter3 in xrange(dim1)])

    config = {'fs': freq, 'hour': hour, 'names': name_c,
              'posgain': positivegain, 'neggain': negativegain}
    #config = {'fs': freq, 'hour': hour, 'names': name_c,
    #'temp': temp}

    return all_sig, config

def rrdet(ecg):
    base = Base()
    try:
        thr = base.thr
        fs = base.fs
        lc = base.lc
        uc = base.uc
    except AttributeError:
        return None, None

    B, A = scipy.signal.butter(4, [2 * lc / fs, 2 * uc / fs], btype="pass")
    ecgf = scipy.signal.filtfilt(B, A, ecg)

    ecgd = np.diff(ecgf)
    peaks = [itr + 1 for itr in xrange(len(ecgf)) if  ecg[itr] >= thr
             and (ecgd[itr] > 0 and ecgd[itr + 1] < 0 or ecgd[itr] ==0)]

    rri = np.diff(peaks)
    t = np.cumsum(rri) / 1000.0

    return t, rri

class Base:
    def getval(self):
        self.thr = float(self.entry1.get().strip())
        self.fs = float(self.entry2.get().strip())
        self.lc = float(self.entry3.get().strip())
        self.uc = float(self.entry4.get().strip())
        self.master.destroy()
        #return [thr, fs, lc, uc]


    def kill_Tk(self):
        self.master.destroy()


    def __init__(self):

        self.master = Tkinter.Tk()
        self.master.title("RRi Detection Parameters")
        self.master.geometry("250x250")

        frame1 = Tkinter.Frame(self.master)
        frame2 = Tkinter.Frame(self.master)
        frame3 = Tkinter.Frame(self.master)
        frame4 = Tkinter.Frame(self.master)

        label1 = Tkinter.Label(frame1, text="Threshold")
        label2 = Tkinter.Label(frame2, text="Sampling Frequency")
        label3 = Tkinter.Label(frame3, text="Lower Cut-off Frequency")
        label4 = Tkinter.Label(frame4, text="Upper Cut-off Frequency")

        label1.pack()
        label2.pack()
        label3.pack()
        label4.pack()

        self.entry1 = Tkinter.Entry(frame1)
        self.entry2 = Tkinter.Entry(frame2)
        self.entry3 = Tkinter.Entry(frame3)
        self.entry4 = Tkinter.Entry(frame4)

        self.entry1.pack()
        self.entry2.pack()
        self.entry3.pack()
        self.entry4.pack()

        frame1.pack()
        frame2.pack()
        frame3.pack()
        frame4.pack()

        btok = Tkinter.Button(self.master, text="OK", command=self.getval)
        btcan = Tkinter.Button(self.master, text="Cancel", command=self.kill_Tk)
        btok.pack()
        btcan.pack()
        #btok.pack(side="left", padx=50, pady=4)
        #btcan.pack(side="left")

        self.master.mainloop()
