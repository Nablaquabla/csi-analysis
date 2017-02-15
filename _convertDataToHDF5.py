#!/usr/bin/env python
import sys
import pytz
import h5py
import numpy as np
import datetime
import os

# ============================================================================
#                       Full timestamp conversion
# ============================================================================
# Prepare timezones and beginning of epcoch for later use
utc = pytz.utc
eastern = pytz.timezone('US/Eastern')
epochBeginning = utc.localize(datetime.datetime(1970,1,1))

# Convert string to eastern timestamp, convert to UTC timestamp, convert to seconds in epoch
def convertTimestamp(x):
    eastern_ts = eastern.localize(datetime.datetime.strptime(str(np.uint64(x)), '%y%m%d%H%M%S%f'))
    utc_ts = eastern_ts.astimezone(utc)
    sSE = (utc_ts - epochBeginning).total_seconds()
    return sSE

# Vectorize timestamp conversion for faster processing
ct = np.vectorize(convertTimestamp)


def main(argv):
    mainDir = argv[1]
    run = argv[2]
    d = argv[3]

    # Check that day analyzed is a normal day, i.e. no DST changes - Not necessary right now,
    # as there was no data being recorded during the fall change. And this is the only time
    # with ambiguous timestamps

#    tNow = datetime.datetime(2000 + int(d[:2]), int(d[2:4]), int(d[4:6]))
#    easternNow = eastern.localize(tNow)
#    easternTomorrow = eastern.localize(tNow + datetime.timedelta(days=1))
#    elapsedSeconds = easternTomorrow - easternNow
#    noDSTChange = (elapsedSeconds == 86400)


    # Add dataset / group to the hdf5 file
    # Vanilla = Old analysis, using a global baseline estimate
    # CMF = Conditional mean filtered baseline estimate
    # LBL = Local baseline estimate based on 1 us before signal onset
    keys = ['timestamp','overflow-flag','muon-veto-flag','linear-gate-flag','median-csi-baseline','average-csi-baseline','std-csi-baseline',
            'vanilla-pt-peaks','vanilla-roi-peaks','vanilla-iw-peaks','vanilla-arrival-index','vanilla-charge','vanilla-rt-10','vanilla-rt-50','vanilla-rt-90',
            'cmf-pt-peaks','cmf-roi-peaks','cmf-iw-peaks','cmf-arrival-index','cmf-charge','cmf-rt-10','cmf-rt-50','cmf-rt-90',
            'lbl-charge','lbl-rt-10','lbl-rt-50','lbl-rt-90',
            'muon-index']

    # What data type is necessary to save the information provided in the csv files. Mainly used to save some storage space
    datatypes = {'timestamp': np.dtype(np.float),
                 'overflow-flag': np.dtype(np.uint8),
                 'muon-veto-flag': np.dtype(np.uint8),
                 'linear-gate-flag': np.dtype(np.uint8),
                 'median-csi-baseline': np.dtype(np.int16),
                 'average-csi-baseline': np.dtype(np.float),
                 'std-csi-baseline': np.dtype(np.float),

                 'vanilla-pt-peaks': np.dtype(np.uint16),
                 'vanilla-roi-peaks': np.dtype(np.uint16),
                 'vanilla-iw-peaks': np.dtype(np.uint16),
                 'vanilla-arrival-index': np.dtype(np.uint16),
                 'vanilla-charge': np.dtype(np.float),
                 'vanilla-rt-10': np.dtype(np.float),
                 'vanilla-rt-50': np.dtype(np.float),
                 'vanilla-rt-90': np.dtype(np.float),

                 'cmf-pt-peaks': np.dtype(np.uint16),
                 'cmf-roi-peaks': np.dtype(np.uint16),
                 'cmf-iw-peaks': np.dtype(np.uint16),
                 'cmf-arrival-index': np.dtype(np.uint16),
                 'cmf-charge': np.dtype(np.float),
                 'cmf-rt-10': np.dtype(np.float),
                 'cmf-rt-50': np.dtype(np.float),
                 'cmf-rt-90': np.dtype(np.float),

                 'lbl-charge': np.dtype(np.float),
                 'lbl-rt-10': np.dtype(np.float),
                 'lbl-rt-50': np.dtype(np.float),
                 'lbl-rt-90': np.dtype(np.float),

                 'muon-index': np.dtype(np.uint16)}

    # Create output HDF5 file
    f = h5py.File('%s/%s/%s.h5'%(mainDir,run,d),'w')

    # Get all output file times using the 'B-' files and sort the output
    times = [x.split('-')[1] for x in os.listdir('%s/%s/%s'%(mainDir,run,d)) if 'B-' in x]
    times = np.sort(np.asarray(times))
    subTimeArray = []
    tFirst = eastern.localize(datetime.datetime(2015,1,1,int(times[0][:2]),int(times[0][2:4]),int(times[0][4:6])))
    tLast = eastern.localize(datetime.datetime(2015,1,1,int(times[-1][:2]),int(times[-1][2:4]),int(times[-1][4:6])))

    # Split data sets into chunks of 30 minutes - If the last chunk would have
    # less than 15 minutes in it add it to the previous one
    currentHour = tFirst
    _tmpSubT = []
    for tm in times:
        tCurrent = eastern.localize(datetime.datetime(2015,1,1,int(tm[:2]),int(tm[2:4]),int(tm[4:6])))
        deltaT = (tCurrent - currentHour).total_seconds()
        if deltaT <= 1800.0:
            _tmpSubT.append(tm)
        else:
            if (tLast - tCurrent).total_seconds() <= 2700.0:
                _tmpSubT.append(tm)
            else:
                subTimeArray.append(_tmpSubT)
                _tmpSubT = [tm]
                currentHour = tCurrent
    if len(_tmpSubT) > 0:
        subTimeArray.append(_tmpSubT)

    # For each sub-time merge all distribution data and concatenate the
    # important numbers
    for sTA in subTimeArray:
        waveformCounter = []
        linearGateCounter = []
        overflowCounter = []
        muonVetoCounter = []
        averageBaseline = []

        peakCharge = {'vanilla': np.zeros(300),
                      'cmf': np.zeros(300),
                      'lbl': np.zeros(300)}

        peakAmplitude = {'vanilla': np.zeros(51),
                         'cmf': np.zeros(51),
                         'lbl': np.zeros(51)}

        peakWidth = {'vanilla': np.zeros(51),
                     'cmf': np.zeros(51)}

        peakB = {'vanilla': {'pt': np.zeros(51), 'roi': np.zeros(51), 'iw': np.zeros(51)},
                 'cmf': {'pt': np.zeros(51), 'roi': np.zeros(51), 'iw': np.zeros(51)}}

        peakS = {'vanilla': {'pt': np.zeros(51), 'roi': np.zeros(51), 'iw': np.zeros(51)},
                 'cmf': {'pt': np.zeros(51), 'roi': np.zeros(51), 'iw': np.zeros(51)}}

        muonEventIndices = np.array([])

        # Read data from file...
        for t in sTA:
            if os.stat('%s/%s/%s/%s-%s'%(mainDir,run,d,'I',t)) > 0 and os.path.getsize('%s/%s/%s/%s-%s'%(mainDir,run,d,'S',t)) > 0:
                with open('%s/%s/%s/%s-%s'%(mainDir,run,d,'I',t),'r') as fIn:
                    for idx,line in enumerate(fIn):
                        if idx == 0:
                            data = np.array(line.split())
                            waveformCounter.append(int(data[0]))
                            linearGateCounter.append(int(data[1]))
                            overflowCounter.append(int(data[2]))
                            muonVetoCounter.append(int(data[3]))
                            averageBaseline.append(float(data[4]))
                        if idx == 2:
                            peakCharge['vanilla'] = peakCharge['vanilla'] + np.array(line.split(),dtype=int)
                        if idx == 4:
                            peakAmplitude['vanilla'] = peakAmplitude['vanilla'] + np.array(line.split(),dtype=int)
                        if idx == 6:
                            peakWidth['vanilla'] = peakWidth['vanilla'] + np.array(line.split(),dtype=int)
                        if idx == 8:
                            peakB['vanilla']['pt'] = peakB['vanilla']['pt'] + np.array(line.split(),dtype=int)
                        if idx == 10:
                            peakB['vanilla']['roi'] = peakB['vanilla']['roi'] + np.array(line.split(),dtype=int)
                        if idx == 12:
                            peakB['vanilla']['iw'] = peakB['vanilla']['iw'] + np.array(line.split(),dtype=int)
                        if idx == 14:
                            peakS['vanilla']['pt'] = peakS['vanilla']['pt'] + np.array(line.split(),dtype=int)
                        if idx == 16:
                            peakS['vanilla']['roi'] = peakS['vanilla']['roi'] + np.array(line.split(),dtype=int)
                        if idx == 18:
                            peakS['vanilla']['iw'] = peakS['vanilla']['iw'] + np.array(line.split(),dtype=int)
                        if idx == 20:
                            peakCharge['lbl'] = peakCharge['lbl'] + np.array(line.split(),dtype=int)
                        if idx == 22:
                            peakAmplitude['lbl'] = peakAmplitude['lbl'] + np.array(line.split(),dtype=int)
                        if idx == 24:
                            peakCharge['cmf'] = peakCharge['cmf'] + np.array(line.split(),dtype=int)
                        if idx == 26:
                            peakAmplitude['cmf'] = peakAmplitude['cmf'] + np.array(line.split(),dtype=int)
                        if idx == 28:
                            peakWidth['cmf'] = peakWidth['cmf'] + np.array(line.split(),dtype=int)
                        if idx == 30:
                            peakB['cmf']['pt'] = peakB['cmf']['pt'] + np.array(line.split(),dtype=int)
                        if idx == 32:
                            peakB['cmf']['roi'] = peakB['cmf']['roi'] + np.array(line.split(),dtype=int)
                        if idx == 34:
                            peakB['cmf']['iw'] = peakB['cmf']['iw'] + np.array(line.split(),dtype=int)
                        if idx == 36:
                            peakS['cmf']['pt'] = peakS['cmf']['pt'] + np.array(line.split(),dtype=int)
                        if idx == 38:
                            peakS['cmf']['roi'] = peakS['cmf']['roi'] + np.array(line.split(),dtype=int)
                        if idx == 40:
                            peakS['cmf']['iw'] = peakS['cmf']['iw'] + np.array(line.split(),dtype=int)
                        if idx == 42:
                            muonEventIndices = np.concatenate((muonEventIndices,np.array(line.split(),dtype=int)))

        if len(waveformCounter) > 0:
            f.create_dataset('/I/%s/waveformCounter'%sTA[0],data=waveformCounter)
            f.create_dataset('/I/%s/linearGateCounter'%sTA[0],data=linearGateCounter)
            f.create_dataset('/I/%s/overflowCounter'%sTA[0],data=overflowCounter)
            f.create_dataset('/I/%s/muonVetoCounter'%sTA[0],data=muonVetoCounter)
            f.create_dataset('/I/%s/averageBaseline'%sTA[0],data=averageBaseline)
            f.create_dataset('/I/%s/muonEventIndices'%sTA[0],data=muonEventIndices)

            for analysisType in ['vanilla','cmf','lbl']:
                f.create_dataset('/I/%s/peakCharge/%s'%(sTA[0],analysisType),data=peakCharge[analysisType])
                f.create_dataset('/I/%s/peakAmplitude/%s'%(sTA[0],analysisType),data=peakAmplitude[analysisType])

            for analysisType in ['vanilla','cmf']:
                f.create_dataset('/I/%s/peakWidth/%s'%(sTA[0],analysisType),data=peakWidth[analysisType])
                for region in ['pt','roi','iw']:
                    f.create_dataset('/I/%s/peaksInB/%s/%s'%(sTA[0],analysisType,region),data=peakB[analysisType][region])
                    f.create_dataset('/I/%s/peaksInS/%s/%s'%(sTA[0],analysisType,region),data=peakS[analysisType][region])

    for w in ['B','S']:
        create_Dataset = True

        # Used for appending to resized arrays
        appendIdxWithEvent = 0
        appendIdxWithoutEvent = 0

        # Data sets created in the HDF5 file
        dset = {}

        f.create_group(w)
        for idx,t in enumerate(times):
            try:
                # Check that file actually contains triggers
                if os.path.getsize('%s/%s/%s/%s-%s'%(mainDir,run,d,w,t)) > 0:

                    # Read data and check convert data files with a single entry to arrays
                    _tdata = np.loadtxt('%s/%s/%s/%s-%s'%(mainDir,run,d,w,t)).T
                    if np.isscalar(_tdata[0]):
                        _tdata = np.array([np.array([x]) for x in _tdata])

                    # Convert timestamps to seconds since epoch (UTC)
                    _tdata[0] = ct(_tdata[0])

                    # Split data into triggers with and without events
                    noEventsInROI = (_tdata[10] == -1)
                    eventsInROI = np.logical_not(noEventsInROI)

                    triggersWithoutEvents = _tdata[0][noEventsInROI]
                    triggersWithEvents = _tdata.T[eventsInROI].T

                    if create_Dataset:
                        create_Dataset = False
                        for i,k in enumerate(keys):
                            dset[k] = f.create_dataset('/%s/%s'%(w,k),data=triggersWithEvents[i],dtype=datatypes[k],maxshape=(None,))
                        dset['no-event'] = f.create_dataset('/%s/no-event'%(w),data=triggersWithoutEvents,dtype=datatypes['timestamp'],maxshape=(None,))
                    else:
                        for i,k in enumerate(keys):
                            dset[k].resize((appendIdxWithEvent + len(triggersWithEvents[i]),))
                            dset[k][appendIdxWithEvent:] = triggersWithEvents[i]
                        dset['no-event'].resize((appendIdxWithoutEvent+len(triggersWithoutEvents),))
                        dset['no-event'][appendIdxWithoutEvent:] = triggersWithoutEvents

                    appendIdxWithEvent = dset['timestamp'].shape[0]
                    appendIdxWithoutEvent = dset['no-event'].shape[0]

                    del _tdata
                else:
                    continue
            except OSError:
                 continue
    f.close()

if __name__ == '__main__':
    main(sys.argv)
