#!/usr/bin/env python
import os
import numpy as np
mainDir = '/data2/coherent/data/csi/bjs-analysis/'
#runDirs = [x for x in os.listdir(mainDir) if 'Run' in x]
#runDirs = ['Run-17-03-20-18-01-09']
# Am analysis
#runDirs = ['Position-%d'%x for x in np.arange(1,10)]
#runDirs = ['Run-17-03-27-13-26-45']
#    runDirs = ['Run-17-04-05-18-47-04','Run-17-04-10-11-14-04']
#    runDirs = ['Run-17-04-17-16-14-23','Run-17-04-24-10-13-09','Run-17-05-01-09-57-15']
#    runDirs = ['Run-17-05-08-09-34-23','Run-17-05-09-14-09-13']
#runDirs = ['Run-17-04-05-18-47-04','Run-17-04-10-11-14-04','Run-17-04-17-16-14-23',
#           'Run-17-04-24-10-13-09','Run-17-05-01-09-57-15','Run-17-05-08-09-34-23',
#           'Run-17-05-09-14-09-13']
#runDirs = ['Run-17-05-15-11-54-49']
#runDirs = ['Run-17-05-18-12-43-56']

#runDirs = ['Run-15-03-27-12-42-26','Run-15-03-30-13-33-05','Run-15-04-08-11-38-28',
#           'Run-15-04-17-16-56-59','Run-15-04-29-16-34-44','Run-15-05-05-16-09-12',
#           'Run-15-05-11-11-46-30','Run-15-05-19-17-04-44','Run-15-05-27-11-13-46']
#runDirs = ['Run-17-05-18-12-43-56']
runDirs = ['Run-17-05-22-09-58-19']


 



for rD in runDirs:
    hdfFiles = [x for x in os.listdir(mainDir + rD) if 'h5' in x]
    if len(hdfFiles) > 0:
        processedDir = mainDir + 'Processed/%s'%rD
        if not os.path.exists(processedDir):
             os.makedirs(processedDir)
        for hF in hdfFiles:
            moveCmd = 'mv %s%s/%s %s/'%(mainDir,rD,hF,processedDir)
            os.system(moveCmd)
