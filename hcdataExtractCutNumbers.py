#!/usr/bin/env python

import h5py
import numpy as np
import os
import sys
import pytz
import datetime

dataKeys = ['timestamp','median-csi-baseline','average-csi-baseline','std-csi-baseline',
            'vanilla-pt-peaks','vanilla-roi-peaks','vanilla-iw-peaks','vanilla-arrival-index','vanilla-charge','vanilla-rt-10','vanilla-rt-50','vanilla-rt-90',
            'cmf-pt-peaks','cmf-roi-peaks','cmf-iw-peaks','cmf-arrival-index','cmf-charge','cmf-rt-10','cmf-rt-50','cmf-rt-90',
            'lbl-charge','lbl-rt-10','lbl-rt-50','lbl-rt-90','beam-power']

def main(argv):
    mainDir = argv[1]
    run = argv[2]
    excludeTimeFile = argv[3]

    excludeTimes = np.loadtxt(excludeTimeFile,dtype=str)

    # Define timezones used in analysis
    eastern = pytz.timezone('US/Eastern')
    utc = pytz.utc
    epochBeginning = utc.localize(datetime.datetime(1970,1,1))

    # Read times that shall be excluded from the analysis
    excludeTimes = np.loadtxt(excludeTimeFile,dtype=str)
    exTS = []
    for t in excludeTimes:
        exTS.append([(eastern.localize(datetime.datetime.strptime(x,'%Y-%m-%d-%H-%M-%S')).astimezone(utc)-epochBeginning).total_seconds() for x in t])

    # Create/open stability HDF5 file that contains all stability data
    h5Out = h5py.File(mainDir + '/Trigger-Numbers/%s-Trigger-Numbers.h5'%run,'w')

    # Determine all days in run folder that need to be analyzed
    h5Days = [x for x in np.sort(os.listdir(os.path.join(mainDir,run))) if '.h5' in x]

    # For each day get the times and the corresponding SPEQ fits
    for day in h5Days:

        # Prepare mv, o, l flag data:
        flags = {'MV': 0, 'O': 0, 'LG': 0, 'WF': 0}

        # Setup new info dict that contains how many triggers have been analyzed per day and how much power has been accumulated
        infoData = {}
        for wd in ['S','B']:
            infoData[wd] = {'total-triggers': 0,
                            'total-triggers-wo-drops': 0,
                            'total-triggers-wo-flags': 0,
                            'on-triggers-wo-flags': 0,
                            'off-triggers-wo-flags': 0,
                            'on-triggers-w-C': 0,
                            'off-triggers-w-C': 0,
                            'on-triggers-w-C-PT': 0,
                            'off-triggers-w-C-PT': 0,
                            'on-triggers-w-C-PT-RT': 0,
                            'off-triggers-w-C-PT-RT': 0}

        d = day.split('.')[0]
        h5In = h5py.File(os.path.join(mainDir,run,day),'r')
        speqCharge = h5In['/SPEQ/lbl/PolyaBest'][...][:,0]

        for time in h5In['/I/'].keys():
            flags['MV'] += np.sum(h5In['/I/%s/muonVetoCounter'%time])
            flags['O'] += np.sum(h5In['/I/%s/overflowCounter'%time])
            flags['LG'] += np.sum(h5In['/I/%s/linearGateCounter'%time])
            flags['WF'] += np.sum(h5In['/I/%s/waveformCounter'%time])

        nFlagsWEvents = {'O':  {'on': 0, 'off': 0},
                         'MV': {'on': 0, 'off': 0},
                         'LG': {'on': 0, 'off': 0}}

        for wd in ['S','B']:
            # ================================================
            # Working with no event data (<4 PIW && < 20 PE Q)
            # ================================================

            # Get info data for waveforms without any event
            noEventTimestamps = h5In['/%s/no-event'%wd][...]
            noEventPower = h5In['/%s/no-event-beam-power'%wd][...]

            # Increase total number of triggers
            infoData[wd]['total-triggers'] += len(noEventTimestamps)

            # Find times that are excluded in the analysis
            timeExclusionCut = np.zeros(len(noEventTimestamps))
            for t in exTS:
                timeExclusionCut = timeExclusionCut + np.asarray((noEventTimestamps >= t[0]) * (noEventTimestamps <= t[1]),dtype=int)
            timeExclusionCut = np.logical_not(np.asarray(timeExclusionCut,dtype=bool))

            # Cut times that are excluded and divide data into power on and off subsets
            currentPower = noEventPower[timeExclusionCut]
            beamOn = (currentPower > 10)
            beamOff = (currentPower <= 10) * (currentPower >= -0.1)
            beamBad = (currentPower == -1)

            infoData[wd]['total-triggers-wo-drops'] += len(currentPower) - np.sum(beamBad)
            infoData[wd]['total-triggers-wo-flags'] += len(currentPower) - np.sum(beamBad) # Flags will be subtracted later
            infoData[wd]['on-triggers-wo-flags'] += np.sum(beamOn) # Flags will be subtracted later
            infoData[wd]['off-triggers-wo-flags'] += np.sum(beamOff) # Flags will be subtracted later

            # ================================================
            # Working with event data (>=4 PIW || >=20 PE Q)
            # ================================================

            timestamps = h5In['/%s/timestamp'%wd][...]
            peaksInROI = h5In['/%s/vanilla-roi-peaks'%wd][...]
            peaksInIW = h5In['/%s/vanilla-iw-peaks'%wd][...]
            peaksInPT = h5In['/%s/vanilla-pt-peaks'%wd][...]
            rt1090 = h5In['/%s/lbl-rt-90'%wd][...] - h5In['/%s/lbl-rt-10'%wd][...]
            rt050 = h5In['/%s/lbl-rt-50'%wd][...]
            charge = h5In['/%s/lbl-charge'%wd][...]
            speqIdx = h5In['/%s/speQindex'%wd][...]
            NPE = charge/speqCharge[speqIdx]
            arrivalIndex = h5In['/%s/vanilla-arrival-index'%wd][...]
            power = h5In['/%s/beam-power'%wd][...]
            overflow = h5In['/%s/overflow-flag'%wd][...]
            muonVeto = h5In['/%s/muon-veto-flag'%wd][...]
            linearGate = h5In['/%s/linear-gate-flag'%wd][...]
            avgBaseline = h5In['/%s/average-csi-baseline'%wd][...]
            stdBaseline = h5In['/%s/std-csi-baseline'%wd][...]
            NPE[np.isnan(NPE)] = -1

            # Increase total number of triggers
            infoData[wd]['total-triggers'] += len(timestamps)

            # Remove data within any excluded time window
            timeExclusionCut = np.zeros(len(timestamps))
            for t in exTS:
                timeExclusionCut = timeExclusionCut + np.asarray((timestamps >= t[0]) * (timestamps <= t[1]),dtype=int)
            timeExclusionCut = np.logical_not(np.asarray(timeExclusionCut,dtype=bool))

            if np.any(timeExclusionCut):
                currentPower = power[timeExclusionCut]
                beamOn = (currentPower > 10)
                beamOff = (currentPower <= 10) * (currentPower >= -0.1)
                beamBad = (currentPower == -1)

                nFlagsWEvents['O']['on'] += np.sum((overflow[timeExclusionCut] == 1) * beamOn)
                nFlagsWEvents['O']['off'] += np.sum((overflow[timeExclusionCut] == 1) * beamOff)
                nFlagsWEvents['MV']['on'] += np.sum((muonVeto[timeExclusionCut] == 1) * beamOn)
                nFlagsWEvents['MV']['off'] += np.sum((muonVeto[timeExclusionCut] == 1) * beamOff)
                nFlagsWEvents['LG']['on'] += np.sum((linearGate[timeExclusionCut] == 1) * beamOn)
                nFlagsWEvents['LG']['off'] += np.sum((linearGate[timeExclusionCut] == 1) * beamOff)

                infoData[wd]['total-triggers-wo-drops'] += len(currentPower) - np.sum(beamBad)
                infoData[wd]['total-triggers-wo-flags'] += len(currentPower) - np.sum(beamBad) # Flags will be subtracted later

                infoData[wd]['on-triggers-wo-flags'] += np.sum(beamOn) # Flags will be subtracted later
                infoData[wd]['off-triggers-wo-flags'] += np.sum(beamOff) # Flags will be subtracted later

                # Simple flag cuts
                cutLinGate = linearGate == 0
                cutMuonVeto = muonVeto == 0
                cutOverflow = overflow == 0
                cutNAN = NPE >= 0

                # Apply actual data cuts
                cutIW = np.logical_or((peaksInIW >= 8),(NPE >= 30))
                cutPT = peaksInPT <= 3
                cRT1 = rt050 < rt1090
                cRT2 = (rt050 >= 100) * (rt050 <= 1250)
                cRT3 = (rt1090 >= 250) * (rt1090 <= 1425)
                cutRT = cRT1* cRT2 * cRT3

                # Cutting only Cherenkov
                cutCOn = (cutIW * cutLinGate * cutMuonVeto * cutOverflow * cutNAN)[timeExclusionCut] * beamOn
                cutCOff = (cutIW * cutLinGate * cutMuonVeto * cutOverflow * cutNAN)[timeExclusionCut] * beamOff
                infoData[wd]['on-triggers-w-C'] += np.sum(cutCOn)
                infoData[wd]['off-triggers-w-C'] += np.sum(cutCOff)

                # Cutting Cherenkov & Pretrace
                cutCPTOn = (cutIW * cutLinGate * cutMuonVeto * cutOverflow * cutNAN * cutPT)[timeExclusionCut] * beamOn
                cutCPTOff = (cutIW * cutLinGate * cutMuonVeto * cutOverflow * cutNAN * cutPT)[timeExclusionCut] * beamOff
                infoData[wd]['on-triggers-w-C-PT'] += np.sum(cutCPTOn)
                infoData[wd]['off-triggers-w-C-PT'] += np.sum(cutCPTOff)

                # Cutting Cherenkov & Pretrace & Risetime
                cutCPTOn = (cutIW * cutLinGate * cutMuonVeto * cutOverflow * cutNAN * cutPT * cutRT)[timeExclusionCut] * beamOn
                cutCPTOff = (cutIW * cutLinGate * cutMuonVeto * cutOverflow * cutNAN * cutPT * cutRT)[timeExclusionCut] * beamOff
                infoData[wd]['on-triggers-w-C-PT-RT'] += np.sum(cutCPTOn)
                infoData[wd]['off-triggers-w-C-PT-RT'] += np.sum(cutCPTOff)

#        print nFlagsWEvents
        # Subtract vetoed triggers fromt he total number of events
        for wd in ['S','B']:
            infoData[wd]['total-triggers-wo-flags'] -= (flags['O'] + flags['LG'] + flags['MV'])

        # Subtract vetoed triggers fromt he total number of events
        for wd in ['S','B']:

            infoData[wd]['on-triggers-wo-flags'] -= int(np.ceil(flags['O']*(1.0*nFlagsWEvents['O']['on']/(nFlagsWEvents['O']['on']+nFlagsWEvents['O']['off'])) +
                                                     flags['LG']*(1.0*nFlagsWEvents['LG']['on']/(nFlagsWEvents['LG']['on']+nFlagsWEvents['LG']['off'])) +
                                                     flags['MV']*(1.0*nFlagsWEvents['MV']['on']/(nFlagsWEvents['MV']['on']+nFlagsWEvents['MV']['off']))))
            infoData[wd]['off-triggers-wo-flags'] -= int(np.ceil(flags['O']*(1.0*nFlagsWEvents['O']['off']/(nFlagsWEvents['O']['on']+nFlagsWEvents['O']['off'])) +
                                                     flags['LG']*(1.0*nFlagsWEvents['LG']['off']/(nFlagsWEvents['LG']['on']+nFlagsWEvents['LG']['off'])) +
                                                     flags['MV']*(1.0*nFlagsWEvents['MV']['off']/(nFlagsWEvents['MV']['on']+nFlagsWEvents['MV']['off']))))

            deltaTrigs = infoData[wd]['on-triggers-wo-flags'] + infoData[wd]['off-triggers-wo-flags'] - infoData[wd]['total-triggers-wo-flags']
            if deltaTrigs < 0:
                if infoData[wd]['off-triggers-wo-flags'] < infoData[wd]['on-triggers-wo-flags']:
                    infoData[wd]['off-triggers-wo-flags'] += np.abs(deltaTrigs)
                else:
                    infoData[wd]['on-triggers-wo-flags'] += np.abs(deltaTrigs)
            elif deltaTrigs > 0:
                if infoData[wd]['off-triggers-wo-flags'] > infoData[wd]['on-triggers-wo-flags']:
                    infoData[wd]['off-triggers-wo-flags'] -= np.abs(deltaTrigs)
                else:
                    infoData[wd]['on-triggers-wo-flags'] -= np.abs(deltaTrigs)


        print 'Total Triggers: ', infoData['S']['total-triggers']
        print 'Triggers after time and bad power cuts: ', infoData['S']['total-triggers-wo-drops']
        print 'Triggers after flag cuts: ', infoData['S']['total-triggers-wo-flags']
        print 'On/Off triggers after flag cuts: ', infoData['S']['on-triggers-wo-flags'], infoData['S']['off-triggers-wo-flags'], infoData['S']['on-triggers-wo-flags'] + infoData['S']['off-triggers-wo-flags']
        print 'On/Off triggers after Cherenkov cuts: ', infoData['S']['on-triggers-w-C'], infoData['S']['off-triggers-w-C'], infoData['S']['on-triggers-w-C'] + infoData['S']['off-triggers-w-C']
        print 'On/Off triggers after Pretrace cuts: ', infoData['S']['on-triggers-w-C-PT'], infoData['S']['off-triggers-w-C-PT'], infoData['S']['on-triggers-w-C-PT'] + infoData['S']['off-triggers-w-C-PT']
        print 'On/Off triggers after Risetime cuts: ', infoData['S']['on-triggers-w-C-PT-RT'], infoData['S']['off-triggers-w-C-PT-RT'], infoData['S']['on-triggers-w-C-PT-RT'] + infoData['S']['off-triggers-w-C-PT-RT']
#
#
        for wd in ['S','B']:
            h5Out.create_dataset('/%s/%s/Total-Triggers'%(d,wd), data=infoData[wd]['total-triggers'])
            h5Out.create_dataset('/%s/%s/Triggers-After-Time-And-Power-Cuts'%(d,wd), data=infoData[wd]['total-triggers-wo-drops'])
            h5Out.create_dataset('/%s/%s/Triggers-After-Flag-Cuts'%(d,wd), data=infoData[wd]['total-triggers-wo-flags'])
            h5Out.create_dataset('/%s/%s/On-Triggers-After-Flag-Cuts'%(d,wd), data=infoData[wd]['on-triggers-wo-flags'])
            h5Out.create_dataset('/%s/%s/Off-Triggers-After-Flag-Cuts'%(d,wd), data=infoData[wd]['off-triggers-wo-flags'])
            h5Out.create_dataset('/%s/%s/On-Triggers-After-C-Cuts'%(d,wd), data=infoData[wd]['on-triggers-w-C'])
            h5Out.create_dataset('/%s/%s/Off-Triggers-After-C-Cuts'%(d,wd), data=infoData[wd]['off-triggers-w-C'])
            h5Out.create_dataset('/%s/%s/On-Triggers-After-C-PT-Cuts'%(d,wd), data=infoData[wd]['on-triggers-w-C-PT'])
            h5Out.create_dataset('/%s/%s/Off-Triggers-After-C-PT-Cuts'%(d,wd), data=infoData[wd]['off-triggers-w-C-PT'])
            h5Out.create_dataset('/%s/%s/On-Triggers-After-C-PT-RT-Cuts'%(d,wd), data=infoData[wd]['on-triggers-w-C-PT-RT'])
            h5Out.create_dataset('/%s/%s/Off-Triggers-After-C-PT-RT-Cuts'%(d,wd), data=infoData[wd]['off-triggers-w-C-PT-RT'])

        h5In.close()
    h5Out.close()
# ============================================================================
#                                Run program
# ============================================================================
if __name__ == '__main__':

    mainDir = '/data2/coherent/data/csi/bjs-analysis/Processed/'

#    runDirs = ['Run-15-12-26-08-30-40']
#    runDirs = ['Run-15-09-21-20-58-01']
#    runDirs = ['Run-17-02-08-00-00-00']
#    runDirs = ['Run-17-02-08-16-39-02']
    runDirs = ['Run-15-06-25-12-53-44']
#    runDirs = ['Run-15-11-24-15-35-32']
#    runDirs = ['Run-15-08-18-14-51-18']
#    runDirs = ['Run-15-08-31-00-23-36']
#    runDirs = ['Run-15-10-03-09-26-22']
#    runDirs = ['Run-15-10-29-15-56-36']
#    runDirs = ['Run-15-06-25-12-53-44','Run-15-06-26-11-23-13','Run-15-07-31-18-30-14']
#    runDirs = ['Run-15-08-18-14-51-18','Run-15-08-31-00-23-36']
#    runDirs = ['Run-15-09-23-21-16-00','Run-15-10-03-09-26-22','Run-15-10-13-13-27-09']
#    runDirs = ['Run-15-10-21-13-12-27','Run-15-10-29-15-56-36','Run-15-11-09-11-30-13']
#    runDirs = ['Run-15-11-20-11-34-48','Run-15-11-24-15-35-32','Run-15-12-14-11-21-45']
#    runDirs = ['Run-15-12-26-08-30-40']
#    runDirs = ['Run-16-01-07-12-16-36','Run-16-02-02-16-26-26']
#    runDirs = ['Run-15-12-26-08-30-40','Run-16-01-07-12-16-36','Run-16-02-02-16-26-26']
#    runDirs = ['Run-16-02-15-13-46-34','Run-16-02-29-11-54-20','Run-16-03-09-13-00-14']
#    runDirs = ['Run-16-03-22-18-09-33','Run-16-03-30-12-44-57','Run-16-04-12-11-54-27']
#    runDirs = ['Run-16-04-20-11-22-48','Run-16-05-05-14-08-52','Run-16-05-12-14-07-59']
#    runDirs = ['Run-16-05-17-14-40-34','Run-16-06-02-12-35-56','Run-16-06-17-12-09-12']
#    runDirs = ['Run-16-06-27-17-50-08','Run-16-07-06-18-25-19','Run-16-07-12-11-44-55']
#    runDirs = ['Run-16-07-18-11-50-24','Run-16-07-21-11-59-39','Run-16-07-28-12-49-17']
#    runDirs = ['Run-16-08-04-17-23-52','Run-16-08-09-00-29-54','Run-16-08-16-00-22-26']
#    runDirs = ['Run-16-08-27-11-33-40','Run-16-08-30-11-37-42','Run-16-09-06-15-23-15']
#    runDirs = ['Run-16-09-15-15-23-58']
#    runDirs = ['Run-16-09-26-15-34-10','Run-16-10-04-16-48-32','Run-16-10-07-15-32-53','Run-16-10-18-14-36-17']
#    runDirs = ['Run-17-02-02-17-28-46','Run-17-02-08-16-39-02']
#    runDirs = ['Run-17-02-08-21-55-48','Run-17-02-21-12-39-17']
#    runDirs = ['Run-17-02-21-14-04-51']
#    runDirs = ['Run-17-03-03-11-18-29','Run-17-03-13-11-48-49']
#    runDirs = ['Run-17-02-21-14-04-51']
#    runDirs = ['Run-17-02-02-15-26-34']
#    runDirs = ['Run-15-12-26-08-30-40','Run-16-01-07-12-16-36','Run-16-02-02-16-26-26']
#    runDirs = ['Run-16-11-02-18-39-29','Run-16-11-04-11-08-14']
#    runDirs = ['Run-17-03-20-18-01-09']
#    runDirs = ['Run-17-03-27-13-26-45']
#    runDirs = ['Run-17-04-05-18-47-04','Run-17-04-10-11-14-04']
#    runDirs = ['Run-17-04-17-16-14-23','Run-17-04-24-10-13-09','Run-17-05-01-09-57-15']
#    runDirs = ['Run-17-05-08-09-34-23','Run-17-05-09-14-09-13']

#    argv = ['','F:/Work-Data-Storage/CsI/Condor/SNS/Testdir','Run-15-06-25-12-53-44','E:/GitHub/csi-analysis/excludeTimes.dat']

    for run in runDirs:
        argv = ['',mainDir,run,'/nfs_home/bjo/GitHub/csi-analysis/excludeTimes.dat']
        main(argv)
