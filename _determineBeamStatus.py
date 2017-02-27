#!/home/bjs66/anaconda2/bin/python

import h5py
import numpy as np
import os
import sys
import datetime

def main(argv):

    run = argv[1]
    d = argv[2]
    dataDir = argv[3]
    bphDir = argv[4]

    # Get beam power file and prepare keys for data readout
    bPF = h5py.File('%s/BeamPowerHistory.h5'%bphDir,'r')
    dayTS = datetime.datetime(2000 + int(d[:2]), int(d[2:4]), int(d[4:6]))
    dayTSArray = [dayTS + datetime.timedelta(days=-1), dayTS, dayTS + datetime.timedelta(days=1)]
    dayKeys = [x.strftime('%Y%m%d') for x in dayTSArray]

    # Read power data for current day +/- one day
    timeData = np.array([0])
    powerData = np.array([0])
    for dk in dayKeys:
        timeData = np.concatenate((timeData,bPF['/%s/time'%dk][...]))
        powerData = np.concatenate((powerData,bPF['/%s/power'%dk][...]))

    # Open HDF5 file
    f = h5py.File(dataDir + run + '/' + d + '.h5', 'r+')

    # For both signal and background window go through all events and tag those that happend during a beam on period
    for wd in ['S','B']:

        # If there has already been a beam power check delete the previous data set and replace it with the new one
        if '/%s/beam-power'%wd in f:
            del f['/%s/beam-power'%wd]

        if '/%s/no-event-beam-power'%wd:
            del f['/%s/no-event-beam-power'%wd]

        # Get all event timestamps and truncate them to the second
        evtTS = f['/%s/timestamp'%wd][...].astype(np.uint32)
        noEvtTS = f['/%s/no-event'%wd][...].astype(np.uint32)

        # Array to store beam-on flags
        beamPowerWithEvent = []
        beamPowerWithoutEvent = []

        # Determine power for all triggers w event
        tIdx = 0
        for ets in evtTS:
            if ets == timeData[tIdx]:
                beamPowerWithEvent.append(powerData[tIdx])
            else:
                while timeData[tIdx] < ets:
                    tIdx += 1

        # Determine power for all triggers w/o event
        tIdx = 0
        for nets in noEvtTS:
            if nets == timeData[tIdx]:
                beamPowerWithoutEvent.append(powerData[tIdx])
            else:
                while timeData[tIdx] < nets:
                    tIdx += 1

        # Write beam on flag to HDF5 file
        f.create_dataset('/%s/beam-power'%wd,data=beamPowerWithEvent,dtype=np.float)
        f.create_dataset('/%s/no-event-beam-power'%wd,data=beamPowerWithEvent,dtype=np.float)

    f.close()

# ============================================================================
#                                Run program
# ============================================================================
if __name__ == '__main__':
    main(sys.argv)
