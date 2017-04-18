#!/usr/bin/env python
import h5py
import numpy as np
import easyfit as ef
import sys
import os
import datetime
import pytz

# Define timezones
eastern = pytz.timezone('US/Eastern')
utc = pytz.utc
epochBeginning = utc.localize(datetime.datetime(1970,1,1))


def main(args):
    mainDir = args[1]
    
    runList = [x for x in np.sort(os.listdir(mainDir)) if 'Run' in x]
#    runList = ['Run-15-06-25-12-53-44','Run-15-09-21-20-58-01']
    fOut = h5py.File(mainDir + 'Analyzed/Stability.h5','a')
    
    for run in runList:
        if run in fOut:
            continue

        print run,
        timeArray = []
        baselineArray = []
        linGateArray = []
        overflowArray = []
        muonVetoArray = []
        triggerArray = []
        ptBAcceptanceArray = []
        ptSAcceptanceArray = []
        speqArray = []
        speqErrArray = []
        speqTimeArray = [] 
        powerArray = {'S': [], 'B': []}
        dayList = [x for x in np.sort(os.listdir(os.path.join(mainDir,run))) if '.h5' in x]
        for day in dayList:
            print day
            fIn = h5py.File(os.path.join(mainDir,run,day),'r')
            timesInDay = np.sort(fIn['/I/'].keys())
            _timeArrayForThisDay = []
            for time in timesInDay :
                eTS = eastern.localize(datetime.datetime.strptime(day[:-3]+time,'%y%m%d%H%M%S'))
                uTS = eTS.astimezone(utc)
                sSE = (uTS - epochBeginning).total_seconds()
                timeArray.append(sSE)    
                _timeArrayForThisDay.append(sSE)

                baselineArray.append(np.mean(fIn['/I/%s/averageBaseline'%time]))
                triggerArray.append(np.sum(fIn['/I/%s/waveformCounter'%time]))
                ptBAcceptanceArray.append(np.cumsum(fIn['/I/%s/peaksInB/vanilla/pt/'%time])[:10]/np.sum(fIn['/I/%s/waveformCounter'%time]))
                ptSAcceptanceArray.append(np.cumsum(fIn['/I/%s/peaksInS/vanilla/pt/'%time])[:10]/np.sum(fIn['/I/%s/waveformCounter'%time]))
                linGateArray.append(np.mean(1.0*fIn['/I/%s/linearGateCounter'%time][...]/fIn['/I/%s/waveformCounter'%time][...]))
                overflowArray.append(np.mean(1.0*fIn['/I/%s/overflowCounter'%time][...]/fIn['/I/%s/waveformCounter'%time][...]))
                muonVetoArray.append(np.mean(1.0*fIn['/I/%s/muonVetoCounter'%time][...]/fIn['/I/%s/waveformCounter'%time][...]))
           
            _tPower = {'S': [], 'B': []}          
            for wd in ['S','B']:
                t = fIn['/%s/timestamp'%wd][...]
                tNE = fIn['/%s/no-event'%wd][...]
                tP = fIn['/%s/beam-power'%wd][...]
                tPNE = fIn['/%s/no-event-beam-power'%wd][...]
                cutP = (tP > 10)
                cutPNE = (tPNE > 10)

                for i in range(len(_timeArrayForThisDay)-1):
                    cutT = (t >= _timeArrayForThisDay[i])  * (t < _timeArrayForThisDay[i+1])
                    cutTNE = (tNE >= _timeArrayForThisDay[i]) * (tNE < _timeArrayForThisDay[i+1])
                    powerArray[wd].append((np.sum(tP[cutT*cutP]) + np.sum(tPNE[cutTNE*cutPNE]))/60.0/3600.0/1.0e6)

                cutT = (t > _timeArrayForThisDay[-1])
                cutTNE = (tNE >= _timeArrayForThisDay[-1])
                powerArray[wd].append((np.sum(tP[cutT*cutP]) + np.sum(tPNE[cutTNE*cutPNE]))/60.0/3600.0/1.0e6)

            speqArray.append(fIn['/SPEQ/lbl/PolyaBest/'][...])
            speqErrArray.append(fIn['/SPEQ/lbl/PolyaErr/'][...])
            speqTimeArray.append(fIn['/SPEQ/lbl/Times/'][...])
            fIn.close()
        print 'Done!'
    
        speqArray = [x for sublist in speqArray for x in sublist]
        speqErrArray = [x for sublist in speqErrArray for x in sublist]
        speqTimeArray = [x for sublist in speqTimeArray for x in sublist]
        fOut.create_dataset('/%s/Time'%run, data=timeArray)
        fOut.create_dataset('/%s/Baseline'%run, data=baselineArray)
        fOut.create_dataset('/%s/MuonVetoRate'%run, data=muonVetoArray)
        fOut.create_dataset('/%s/LinearGateRate'%run, data=linGateArray)
        fOut.create_dataset('/%s/OverflowRate'%run, data=overflowArray)
        fOut.create_dataset('/%s/Triggers'%run, data=triggerArray)
        fOut.create_dataset('/%s/PTAcceptanceB'%run, data=ptBAcceptanceArray)
        fOut.create_dataset('/%s/PTAcceptanceS'%run, data=ptSAcceptanceArray)
        fOut.create_dataset('/%s/SPEQ'%run, data=speqArray)
        fOut.create_dataset('/%s/SPEQErr'%run, data=speqErrArray)
        fOut.create_dataset('/%s/SPEQTime'%run, data=speqTimeArray)
        fOut.create_dataset('/%s/Power-S'%run, data=powerArray['S'])
        fOut.create_dataset('/%s/Power-B'%run, data=powerArray['B'])
    fOut.close()

# ============================================================================
#                                Run program
# ============================================================================
if __name__ == '__main__':
#    args = ['', '/home/bjs66/csi/bjs-analysis/','Run-15-06-26-11-23-13','150711']
#    main(args)
    args = ['','/data2/coherent/data/csi/bjs-analysis/Processed/']
    main(args)
















