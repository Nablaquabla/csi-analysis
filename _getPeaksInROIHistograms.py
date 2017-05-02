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
    
#    runList = [x for x in np.sort(os.listdir(mainDir)) if 'Run' in x]
#    runList = ['Run-15-06-25-12-53-44','Run-15-09-21-20-58-01']
#    runList = ['Run-15-06-25-12-53-44']
    runList = ['Run-15-03-27-12-42-26']
    fOut = h5py.File(mainDir + 'Analyzed/PeaksInROI.h5','a')

    nHist = {}
    for nPPT in range(10):
        nHist[nPPT] = np.zeros(100)
    
    nHistAll = {'S': {'ROI': np.zeros(51), 'PT': np.zeros(51)},
                'B': {'ROI': np.zeros(51), 'PT': np.zeros(51)}}

    for run in runList:
        if run in fOut:
            continue

        dayList = [x for x in np.sort(os.listdir(os.path.join(mainDir,run))) if '.h5' in x]
        for day in dayList:
            print day
            fIn = h5py.File(os.path.join(mainDir,run,day),'r')
            for wd in ['S','B']:
                nPROI = fIn['/%s/vanilla-roi-peaks'%wd][...]
                nPPT = fIn['/%s/vanilla-pt-peaks'%wd][...]
            
                for nPPTMax in range(10):
                    cutPT = (nPPT <= nPPTMax)
                    nHist[nPPTMax] = nHist[nPPTMax] + np.histogram(nPROI[cutPT],100,[0,100])[0]
            for time in np.sort(fIn['/I/'].keys()):
                for wd in ['S','B']:
                    nHistAll[wd]['ROI'] = nHistAll[wd]['ROI'] + fIn['/I/%s/peaksIn%s/vanilla/roi'%(time,wd)][...]
                    nHistAll[wd]['PT'] = nHistAll[wd]['PT'] + fIn['/I/%s/peaksIn%s/vanilla/pt'%(time,wd)][...]
            fIn.close()

        for wd in ['S','B']:
            for nPPTMax in range(10):
                fOut.create_dataset('/%s/%s/%d'%(run,wd,nPPTMax),data=nHist[nPPTMax])
            fOut.create_dataset('/%s/%s/ROI'%(run,wd),data=nHistAll[wd]['ROI'])
            fOut.create_dataset('/%s/%s/PT'%(run,wd),data=nHistAll[wd]['PT'])
               
    fOut.close()

# ============================================================================
#                                Run program
# ============================================================================
if __name__ == '__main__':
#    args = ['', '/home/bjs66/csi/bjs-analysis/','Run-15-06-26-11-23-13','150711']
#    main(args)
    args = ['','/data2/coherent/data/csi/bjs-analysis/Processed/']
    main(args)
















