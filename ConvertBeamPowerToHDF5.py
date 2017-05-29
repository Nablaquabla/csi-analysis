#!/usr/bin/env python
import numpy as np
import os
import h5py
import datetime
import copy
import pytz
import matplotlib.pylab as plt

# Set main working dir
dataDir = '/data2/coherent/data/csi/bjs-analysis/BeamPowerHistory/'
outDir = '/data2/coherent/data/csi/bjs-analysis/BeamPowerHistory/'

# Prepare timezones and beginning of epcoch for later use
utc = pytz.utc
eastern = pytz.timezone('US/Eastern')
epochBeginning = utc.localize(datetime.datetime(1970,1,1))

# Prepare output format for timestamps:
fmt = '%Y-%m-%d %H:%M:%S %Z%z'
fmt2 = '%y/%m/%d %H:%M:%S'

# Get all beamPower history files
files = np.sort([x for x in os.listdir(dataDir) if '.dat' in x])
dayStrings = [f[-18:-10] for f in files]
dayUTCTS = [(eastern.localize(datetime.datetime.strptime(f[-18:-10],'%Y%m%d')).astimezone(utc)-epochBeginning).total_seconds() for f in files]

# Fix days with no data -> Beam power = -1
for fIdx in range(len(files)):
    if os.path.getsize(dataDir + files[fIdx]) == 0:
        t = np.arange(dayUTCTS[fIdx],dayUTCTS[fIdx+1],dtype=np.uint32)
        p = -1.0*np.ones(len(t),dtype=np.float)
        with open(dataDir + files[fIdx],'w') as f:
            for tt,pp in zip(t,p):
                f.write('%d %d\n'%(tt,pp))

# Open output HDF5 file:
h5Out = h5py.File(outDir + 'BeamPowerHistory.h5','a')

# Check which days are already in the BPH.h5
cutFiles = np.array([(x[-18:-10] not in h5Out and (int(x[-18:-10]) > 20150623)) for x in files])
iMin = np.argmax(cutFiles) - 1


for fIdx in range(iMin,len(files)-1):
    print files[fIdx][-18:-10]
    if fIdx == iMin:
        prevDay = np.loadtxt(dataDir + files[fIdx-1]).T
        currDay = np.loadtxt(dataDir + files[fIdx]).T
        nextDay = np.loadtxt(dataDir + files[fIdx+1]).T
    else:
        prevDay = currDay
        currDay = nextDay
        nextDay = np.loadtxt(dataDir + files[fIdx+1]).T

    wT = np.arange(dayUTCTS[fIdx],dayUTCTS[fIdx+1])
    wP = np.zeros(len(wT))

    # Data in file does not start at the beginning of the day -> delta T is bigger than 1
    # Determine power value for timestamps missing and get the proper starting point in the
    # full timestamp array
    wIdx = 0
    if currDay[0][0] != dayUTCTS[fIdx]:
        if (prevDay[1][-1] == 0) and (currDay[1][0] == 0):
            while True:
                wP[wIdx] = 0
                wIdx += 1
                if wT[wIdx] == currDay[0][0]:
                    break
        else:
            while True:
                wP[wIdx] = -1
                wIdx += 1
                if wT[wIdx] == currDay[0][0]:
                    break

    # Data onset in
    for i in range(len(currDay[0])):
        if wIdx >= len(wT):
            break
        if currDay[0][i] == wT[wIdx]:
            wP[wIdx] = currDay[1][i]
            wIdx += 1

        elif currDay[0][i] > wT[wIdx]:
            if (currDay[1][i] == 0) and (currDay[1][i-1] == 0):
                while True:
                    wP[wIdx] = 0
                    wIdx += 1
                    if wT[wIdx] == currDay[0][i]:
                        wP[wIdx] = currDay[1][i]
                        wIdx += 1
                        break
            elif (currDay[1][i] > 0) and (currDay[1][i-1] > 0) and (currDay[0][i]-currDay[0][i-1]) <= 5:
                while True:
                    wP[wIdx] = (currDay[1][i] + currDay[1][i-1])/2.0
                    wIdx += 1
                    if wT[wIdx] == currDay[0][i]:
                        wP[wIdx] = currDay[1][i]
                        wIdx += 1
                        break
            else:
                while True:
                    wP[wIdx] = -1
                    wIdx += 1
                    if wT[wIdx] == currDay[0][i]:
                        wP[wIdx] = currDay[1][i]
                        wIdx += 1
                        break

    if wIdx < len(wT) - 1:
        if not ((currDay[1][-1] == 0) and (nextDay[1][0] == 0)):
            for _tIdx in range(wIdx,len(wT)):
                wP[_tIdx] = -1
    if files[fIdx][-18:-10] not in h5Out:
        h5Out.create_dataset('/%s/time'%files[fIdx][-18:-10],data=wT,dtype=np.uint32)
        h5Out.create_dataset('/%s/power'%files[fIdx][-18:-10],data=wP,dtype=np.float)

h5Out.close()
