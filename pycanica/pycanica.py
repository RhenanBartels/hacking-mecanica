"""
    Module to convert the codes from Mecanica software, written in Matlab
    to the free world of Python.
"""

import numpy as np
import Tkinter
import scipy.signal
import matplotlib.pyplot as plt
plt.switch_backend('qt4Agg')
plt.ion()


def impdaspy(filename):

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
        raise Exception("File must have binary extension -> filename.bin")
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
    signal = signal.reshape(dim1, len(signal) / float(dim1), order='F')

    #remove baseline

    all_sig = np.array([signal[iter3] - baseline[iter3]
                        for iter3 in xrange(dim1)])

    config = {'fs': freq, 'hour': hour, 'names': name_c,
              'posgain': positivegain, 'neggain': negativegain}
    #config = {'fs': freq, 'hour': hour, 'names': name_c,
    #'temp': temp}

    return all_sig, config


def p2rri(xis, fs, thr=1):
    xis[xis < thr] = 0
    xis[xis >= thr] = 1
    ct1 = xis[0:-1]
    ct2 = xis[1::]
    ctrl = ct2 - ct1
    pos = np.where(ctrl == 1)[0] + 1
    rri = np.diff(pos) / float(fs)
    t = np.cumsum(rri)
    return t, rri


def detrri(ecg):
    base = Base()
    base.rrdet(ecg)
    base.plotter()
    t = base.t
    rri = base.rri
    return t, rri


class Base:
    def getval(self):
        self.thr = float(self.entry1.get().strip())
        self.fs = float(self.entry2.get().strip())
        self.lc = float(self.entry3.get().strip())
        self.uc = float(self.entry4.get().strip())
        self.master.destroy()

    def kill_Tk(self):
        self.master.destroy()

    def rrdet(self, ecg):
        B, A = scipy.signal.butter(4,
                                   [2 * self.lc / self.fs,
                                    2 * self.uc / self.fs], btype="pass")
        ecgf = scipy.signal.filtfilt(B, A, ecg)
        ecgd = np.diff(ecgf)
        peaks = [itr + 1 for itr in xrange(len(ecgf)) if ecgf[itr] >= self.thr
                 and (ecgd[itr] > 0 and ecgd[itr + 1] < 0 or ecgd[itr] == 0)]
        self.ecgf = ecgf
        self.t_ecg = np.arange(0, len(ecg)) / self.fs
        self.peaks = peaks
        self.rri = np.diff(peaks) / self.fs
        self.t = np.cumsum(self.rri)
        self.peaks_ecg = np.array(peaks)  # Maintain list to append later.
        #self.t = self.t - np.min(self.t)

    def plotter(self):
        #Draw the main figure
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(2, 1, 1)
        self.ax2 = self.fig.add_subplot(2, 1, 2)
        self.ax1.plot(self.t_ecg, self.ecgf)
        #Plot the peaks upon each qrs complex
        self.ax1.plot(self.t_ecg[self.peaks], self.ecgf[self.peaks], 'g.-')
        self.ax1.set_ylabel("ECG (mV)")
        self.ax2.plot(self.t, self.rri, 'k.-')
        self.ax2.set_ylabel("RRi (ms)")
        self.ax2.set_xlabel("Time (s)")

        #Event handling
        self.fig.canvas.mpl_connect("button_press_event", self.onclick)
        self.fig.canvas.mpl_connect("key_press_event", self.close)
        self.fig.canvas.start_event_loop(timeout=-1)

    def onclick(self, event):
        #Find the neares point clicked
        self.xpos = np.argmin(abs(event.xdata * 1000.0 - self.peaks))
        self.ecg_pos = np.argmin(abs(event.xdata - self.t_ecg))
        #If left button clicked
        if event.button == 1 and event.key == 'control':
            #Create the rri series withou the peaks manually excluded
            self.peaks = np.delete(self.peaks, self.xpos)
            self.rri = np.diff(self.peaks) / self.fs
            #self.rri = np.diff(np.delete(self.peaks_ecg, self.repo))
            self.t = np.cumsum(self.rri)
            self.t = self.t - min(self.t)
            xlim_temp = self.ax1.get_xlim()
            self.ax1.cla()
            self.ax1.plot(self.t_ecg, self.ecgf)
            self.ax1.plot(self.t_ecg[self.peaks], self.ecgf[self.peaks], 'g.-')
            self.ax1.set_xlim(xlim_temp)
            self.ax2.cla()
            plt.plot(self.t, self.rri, 'k.-')
            self.ax2.set_xlabel('Time (s)')
            self.ax2.set_ylabel('RRi (ms)')
            #self.drawline()
        elif event.button == 3 and event.key == 'control':
            #Refresh array of peaks to add a new one.
            self.peaks = np.insert(self.peaks, len(self.peaks), self.ecg_pos)
            self.peaks = np.sort(self.peaks)
            self.rri = np.diff(self.peaks) / self.fs
            self.t = np.cumsum(self.rri)
            self.t = self.t - min(self.t)
            xlim_temp = self.ax1.get_xlim()
            self.ax1.cla()
            self.ax1.plot(self.t_ecg, self.ecgf)
            self.ax1.plot(self.t_ecg[self.peaks], self.ecgf[self.peaks], 'g.-')
            self.ax1.set_xlim(xlim_temp)
            self.ax2.set_xlabel('Time (s)')
            self.ax2.set_ylabel('RRi (ms)')

            #Need to refresh self.peaks after manually add a peak.
            #removed peaks are appearing again because self.peaks are not
            #refresh. Maybe remove the new peak from self.repo

            self.ax2.cla()
            plt.plot(self.t, self.rri, 'k.-')
            #self.eraseline()

    def drawpoint(self):
        if self.repo[-1] > 0 and self.repo[-1] < len(self.peaks):
            #self.ax1.plot(self.t_ecg, self.ecgf)
            #self.ax1.plot(self.t_ecg[self.peaks],
                           #self.ecgf[self.peaks], 'g.-')
            pass

    def erasepoint(self):
        if self.repo[-1] > 0 and self.repo[-1] < len(self.peaks):
            pass

    def close(self, event):
        if event.key == 'shift':
            self.fig.canvas.stop_event_loop()

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

        self.entry1.insert(0, "0.35")
        self.entry2.insert(0, "1000")
        self.entry3.insert(0, "5")
        self.entry4.insert(0, "40")

        self.entry1.pack()
        self.entry2.pack()
        self.entry3.pack()
        self.entry4.pack()

        frame1.pack()
        frame2.pack()
        frame3.pack()
        frame4.pack()

        btok = Tkinter.Button(self.master, text="OK", command=self.getval)
        btcan = Tkinter.Button(self.master,
                               text="Cancel", command=self.kill_Tk)
        btok.pack()
        btcan.pack()
        self.repo = []
        self.ecg_repo = []
        #btok.pack(side="left", padx=50, pady=4)
        #btcan.pack(side="left")

        self.master.mainloop()


def leastvariance(time, rri, seg=300.0):
    time = time - min(time)
    v = []
    rriv = []
    ind = np.where(time >= seg)[0][0]
    time_temp = time[0:ind + 1]
    rri_temp = rri[0:ind + 1]
    while time_temp[-1] > seg:
        v.append(np.var(rri_temp))
        rriv.append(rri_temp)
        rri = np.delete(rri, 0)
        time = np.cumsum(rri) / 1000.0
        time = time - min(time)
        try:
            ind = np.where(time >= seg)[0][0]
        except IndexError:
            break
        time_temp = time[0:ind + 1]
        rri_temp = rri[0:ind + 1]
    return rriv[np.where(v == min(v))[0]]


def qfilter(rri, order=4):
    N = len(rri)
    for iter1 in xrange(N - 1):
        if iter1 <= order:
            if rri[iter1] / rri[iter1 + 1] <= 0.8 or rri[iter1] / rri[iter1 + 1]\
                    >= 1.2:
                        rri[iter1] = np.mean(rri[iter1:iter1 + order + 1])
        else:
            if rri[iter1] / rri[iter1 + 1] <= 0.8 or rri[iter1] / rri[iter1 + 1]\
                    >= 1.2:
                        rri[iter1] = np.mean(rri[iter1: iter1 - order - 1])
    return rri


def innoresult(filename):
    try:
        fid = open(filename, 'r')  #Open file
    except IOError:
        print "There's no %s in the current directory" % filename

    print "\t\nOpenning file: %s ......\n" % filename

    fid.seek(340)  #Go to line with variables names
    variables_names = fid.readline().strip().split('\t')  #Remove spaces
    fid.seek(960)  #Go to line with values
    variables_values = fid.readlines()
    variables_values.pop(-1)  #Remove last line with dashes
    variables_values.pop(-1)  #Remove last line with dashes
    #Remove spaces
    variables_values = [itr.strip().split('\t') for itr in variables_values]
    #Transform to a np.array to become easier to handle with the data
    variables_values = np.array(variables_values)
    variables_names = variables_names[0:15]  #Get rid of the rest of file
    variables_values = variables_values[:, 0:15]  #Get rid of the rest of the
                                                  #file
    #Dictionary with variable's names and values.
    results = dict(zip(variables_names, variables_values.T))
    fid.close()  #Close file.
    print "...Done!"

    return results
