#!/usr/bin/env python

import h5py
import numpy as np
import os
import sys
import datetime

def main(argv):

    run = argv[2]
    d = argv[3]
    dataDir = argv[1]
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

        if '/%s/no-event-beam-power'%wd in f:
            del f['/%s/no-event-beam-power'%wd]

        # Get all event timestamps and truncate them to the second
        # SNS beam opeartors think a timestamp corresponds to the second leading up to the stamp
        # I.e. timestamp 10 actually covers the second (9,10]
        evtTS = np.asarray(np.ceil(f['/%s/timestamp'%wd][...]),dtype=np.uint32)
        noEvtTS = np.asarray(np.ceil(f['/%s/no-event'%wd][...]),dtype=np.uint32)

        # Determine minimum and maximum timestamp
        tMin = evtTS[0] if noEvtTS[0] > evtTS[0] else noEvtTS[0]
        tMax = evtTS[-1] if noEvtTS[-1] < evtTS[-1] else noEvtTS[-1]

        # Cut time and beampower array to only contain proper times
        cut = np.array((timeData >= tMin) * (timeData <= tMax),dtype=bool)
        cTime = timeData[cut]
        cPower = powerData[cut]

        # Array to store beam power data
        beamPowerWithEvent = []
        beamPowerWithoutEvent = []


#        # Determine power for all triggers w event
#        for ets in evtTS:
#            beamPowerWithEvent.append(powerData[np.where(ets == timeData)])
#
#        # Determine power for all triggers w/o event
#        for nets in noEvtTS:
#            beamPowerWithoutEvent.append(powerData[np.where(nets == timeData)])

        # Determine power for all triggers w event
        idx = 0
        for evt in evtTS:
            pwr = 0
            while True:
                if evt == cTime[idx]:
                    pwr = cPower[idx]
                    break
                else:
                    if evt > cTime[idx]:
                        idx += 1
                        continue
                    if evt < cTime[idx]:
                        idx -= 1
                        continue
            beamPowerWithEvent.append(pwr)

        # Determine power for all triggers w/o event
        idx = 0
        for evt in noEvtTS:
            pwr = 0
            while True:
                if evt == cTime[idx]:
                    pwr = cPower[idx]
                    break
                else:
                    if evt > cTime[idx]:
                        idx += 1
                        continue
                    if evt < cTime[idx]:
                        idx -= 1
                        continue
            beamPowerWithoutEvent.append(pwr)

        # Write beam on flag to HDF5 file
        f.create_dataset('/%s/beam-power'%wd,data=beamPowerWithEvent,dtype=np.float)
        f.create_dataset('/%s/no-event-beam-power'%wd,data=beamPowerWithoutEvent,dtype=np.float)

    f.close()

# ============================================================================
#                                Run program
# ============================================================================
if __name__ == '__main__':
    main(sys.argv)
