#!/usr/bin/env python
import os

mainDir = '/home/bjs66/csi/bjs-analysis/'
runDirs = ['Run-15-06-25-12-53-44']
#runDirs = ['Run-15-06-26-11-23-13','Run-15-07-31-18-30-14',
#           'Run-16-02-15-13-46-34','Run-16-02-29-11-54-20','Run-16-03-09-13-00-14',
#           'Run-16-03-22-18-09-33','Run-16-03-30-12-44-57','Run-16-04-12-11-54-27',
#           'Run-16-04-20-11-22-48','Run-16-05-05-14-08-52','Run-16-05-12-14-07-59',
#           'Run-16-05-17-14-40-34','Run-16-06-02-12-35-56','Run-16-06-17-12-09-12',
#           'Run-16-06-27-17-50-08','Run-16-07-06-18-25-19','Run-16-07-12-11-44-55',
#           'Run-16-07-18-11-50-24','Run-16-07-21-11-59-39','Run-16-07-28-12-49-17',
#           'Run-16-08-04-17-23-52','Run-16-08-09-00-29-54','Run-16-08-16-00-22-26']
 
for rD in runDirs:
    hdfFiles = [x for x in os.listdir(mainDir + rD) if 'h5' in x]
    if len(hdfFiles) > 0:
        processedDir = mainDir + 'Processed/%s'%rD
        if not os.path.exists(processedDir):
             os.makedirs(processedDir)
        for hF in hdfFiles:
            moveCmd = 'mv %s%s/%s %s/'%(mainDir,rD,hF,processedDir)
            os.system(moveCmd)
