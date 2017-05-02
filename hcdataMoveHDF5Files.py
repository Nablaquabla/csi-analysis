#!/usr/bin/env python
import os
import numpy as np
mainDir = '/data2/coherent/data/csi/bjs-analysis/'
#runDirs = [x for x in os.listdir(mainDir) if 'Run' in x]
#runDirs = ['Run-17-03-20-18-01-09']
# Am analysis
runDirs = ['Position-%d'%x for x in np.arange(1,10)]


for rD in runDirs:
    hdfFiles = [x for x in os.listdir(mainDir + rD) if 'h5' in x]
    if len(hdfFiles) > 0:
        processedDir = mainDir + 'Processed/%s'%rD
        if not os.path.exists(processedDir):
             os.makedirs(processedDir)
        for hF in hdfFiles:
            moveCmd = 'mv %s%s/%s %s/'%(mainDir,rD,hF,processedDir)
            os.system(moveCmd)
