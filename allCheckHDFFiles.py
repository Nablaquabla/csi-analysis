#!/usr/bin/env python
import os
import sys
import h5py

def main(args):
    mainDir = args[1]
    runDirs = [x for x in os.listdir(mainDir) if 'Run' in x]
    for rD in runDirs:
        hFiles = [x for x in os.listdir(os.path.join(mainDir,rD)) if 'h5' in x]
        for hF in hFiles:
            fIn = h5py.File(os.path.join(mainDir,rD,hF),'r')
            if '/B/timestamp' in fIn:
                faultyData = fIn['/B/timestamp'][0] == fIn['/B/timestamp'][1]
            else:
                faultyData = True
            if faultyData:
                print rD,hF
            fIn.close()

if __name__ == '__main__':
    main(sys.argv)
