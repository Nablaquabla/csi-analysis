#!/usr/bin/env python
import numpy as np
import h5py
import os

def main(runDirs):

    mainDataDir = '/data2/coherent/data/csi/bjs-analysis/Processed/'
    
    totalWaveforms = 0
    totalMuonVetos = 0
    totalLinearGates = 0
    totalOverflows = 0

    totalBEvents = 0
    totalSEvents = 0

    for rD in runDirs:
        dayFiles = os.listdir(os.path.join(mainDataDir,rD))
        for dF in dayFiles:
            fIn = h5py.File(os.path.join(mainDataDir,rD,dF),'r')
            for time in fIn['/I/'].keys():
                totalWaveforms += np.sum(fIn['/I/%s/waveformCounter'%time][...])
            totalBEvents += len(fIn['/B/timestamp'][...]) + len(fIn['/B/no-event'][...])             
            fIn.close()
    print totalWaveforms, totalBEvents

if __name__ == "__main__":
    runDirs = ['Run-15-06-25-12-53-44']

    main(runDirs)
