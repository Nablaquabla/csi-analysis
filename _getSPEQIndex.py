#!/home/bjs66/anaconda2/bin/python
"""
Created on Mon Feb 01 15:03:56 2016

@author: Nablaquabla
"""
import h5py
import os
import numpy as np
import easyfit as ef
import sys

# ============================================================================
#                                Run program
# ============================================================================
def main(args):
    mainDir = args[1]
    run = args[2]

    # Declare main and run dirs
    mainDir =
    runDir = mainDir + run

    # Get all days in given run folder
    daysInRun = [x.split('.')[0] for x in os.listdir(runDir)]

    speCharges = {'Time': []}

    # For each day in the run folder read the HDF5 file and fit SPEQ spectra
    for day in daysInRun:
        h5In = h5py.File(runDir + '/' + day + '.h5', 'r+')

        # Get SPE charge fits for the current day
        speCharges['Time'] = h5In['/SPEQ/vanilla/Times'][...]

        # For both signal and background window calculate the number of PE from charge for both gaussian and polya spe dists
        for wd in ['S','B']:

            # Get charge data and timestamps from the hdf5 file
            times = h5In['/%s/timestamp'%wd][...]

            # Variables for getting the correct SPEQ from fits based on the timestamp
            qIdx = 0
            qSize = len(speCharges['Time']) - 1
            qIdxUpdate = True
            speQIdxArray = []
            if qSize == 0:
                qIdxUpdate = False
            # For each event get the timestamp and charge. Get the correct SPEQ and convert the charge to NPE
            for q,t in zip(charge,times):
                if qIdxUpdate:
                    if t >= speCharges['Time'][qIdx+1]:
                        qIdx += 1
                    if qIdx >= qSize:
                        qIdxUpdate = False
                speQIdxArray.append(qIdx)

            h5In.create_dataset('/%s/speQindex'%wd, data=speQIdxArray)

        h5In.close()

# ============================================================================
#                                Run program
# ============================================================================
if __name__ == '__main__':
    main(sys.argv)
















