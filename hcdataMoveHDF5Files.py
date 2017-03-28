#!/usr/bin/env python
import os

mainDir = '/data2/coherent/data/csi/bjs-analysis/'
runDirs = [x for x in os.listdir(mainDir) if 'Run' in x]
for rD in runDirs:
    hdfFiles = [x for x in os.listdir(mainDir + rD) if 'h5' in x]
    if len(hdfFiles) > 0:
        processedDir = mainDir + 'Processed/%s'%rD
        if not os.path.exists(processedDir):
             os.makedirs(processedDir)
        for hF in hdfFiles:
            moveCmd = 'mv %s%s/%s %s/'%(mainDir,rD,hF,processedDir)
            os.system(moveCmd)
