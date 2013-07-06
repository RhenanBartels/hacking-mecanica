"""
    Module to convert the codes from Mecanica software, written in Matlab
    to the free world of Python
"""

import numpy as np
import sys


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

def rrdet(ecg, fs):
    ### Butterworth stuff
    #Create de MultLine Dialog box
    import Tkinter

    #http://www.prasannatech.net/2009/05/tkinter-entry-widget-single-line-text.html
    class Base:
        def getval(self):
            global vals



        def __init__(self):

            master = Tkinter.Tk()
            master.title("RRi Detection Parameters")
            master.geometry("250x200")

            frame1 = Tkinter.Frame(master)
            frame2 = Tkinter.Frame(master)
            frame3 = Tkinter.Frame(master)
            frame4 = Tkinter.Frame(master)

            label1 = Tkinter.Label(frame1, text="Threshold")
            label2 = Tkinter.Label(frame2, text="Sampling Frequency")
            label3 = Tkinter.Label(frame3, text="Lower Cut-off Frequency")
            label4 = Tkinter.Label(frame4, text="Upper Cut-off Frequency")

            label1.pack()
            label2.pack()
            label3.pack()
            label4.pack()

            entry1 = Tkinter.Entry(frame1)
            entry2 = Tkinter.Entry(frame2)
            entry3 = Tkinter.Entry(frame3)
            entry4 = Tkinter.Entry(frame4)a

            entry1.pack()
            entry2.pack()
            entry3.pack()
            entry4.pack()

            frame1.pack()
            frame2.pack()
            frame3.pack()
            frame4.pack()

            bt = Tkinter.Button(master, text="OK", command=get_val)

            master.mainloop()


    ecgd = np.diff(ecgf)
    peaks = [itr + 1 for itr in xrange(len(ecgf)) if  ecg[itr] >= thr
             and (ecgd[itr] > 0 and ecgd[itr + 1] < 0 or ecgd[itr] ==0)]
