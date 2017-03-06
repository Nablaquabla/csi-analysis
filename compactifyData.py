#!/home/bjs66/anaconda2/bin/python

import h5py
import numpy as np
import os

def main(argv):
    mainDir = argv[1]
    run = argv[2]

    # Create/open stability HDF5 file that contains all stability data
#    h5Out = h5py.File(mainDir + '/Metadata/Full-Data.h5','a')

    # Determine all days in run folder that need to be analyzed
    h5Days = [x for x in os.listdir(mainDir + run) if '.h5' in x]

    # For each day get the times and the corresponding SPEQ fits
    for d in h5Days:

        print run,d

        # Open current hdf5 file
        h5In = h5py.File(mainDir + run + '/' + d, 'r')
        timeBins = h5In['/SPEQ/vanilla/Times'][...]

        # Get total number of triggers for Signal and Background regions
        # and determine total power delivered in 10 minute windows
        for wd in ['S','B']:
            noEventsTimeStamps = h5In['/%s/no-event'%wd][...]
            noEventBeamPower = h5In['/%s/no-event-beam-power'%wd][...]

            # Variables for getting the correct SPEQ from fits based on the timestamp
            qIdx = 0
            qSize = len(timeBins) - 1
            qIdxUpdate = True
            powerPerBin = np.zeros(len(timeBins))
            numberOfTriggers = {'with-power': 0, 'without-power': 0, 'bad-power': 0, 'total': 0}
            if qSize == 0:
                qIdxUpdate = False

            # Add beam power to the proper time bins
            numberOfTriggers['total'] += len(noEventBeamPower)
            for t,p in zip(noEventsTimeStamps,noEventBeamPower):
                if qIdxUpdate:
                    if t >= timeBins[qIdx+1]:
                        qIdx += 1
                    if qIdx >= qSize:
                        qIdxUpdate = False
                if p > 0:
                    numberOfTriggers['with-power'] += 1
                    powerPerBin[qIdx] += p
                elif p == 0:
                    numberOfTriggers['without-power'] += 1
                else:
                    numberOfTriggers['bad-power'] += 1

            eventTimeIndex= h5In['/%s/speQindex'%wd][...]
            eventBeamPower = h5In['/%s/beam-power'%wd][...]

            numberOfTriggers['total'] += len(eventBeamPower)
            for qIdx,p in zip(eventTimeIndex,eventBeamPower):
                if p > 0:
                    numberOfTriggers['with-power'] += 1
                    powerPerBin[qIdx] += p
                elif p == 0:
                    numberOfTriggers['without-power'] += 1
                else:
                    numberOfTriggers['bad-power'] += 1
        print powerPerBin
        print np.sum(powerPerBin)/1.0e6/3600.0/60.0
        print numberOfTriggers
# ============================================================================
#                                Run program
# ============================================================================
if __name__ == '__main__':
    mDir = '/home/bjs66/csi/bjs-analysis/'

#    runDirs = ['Run-15-06-25-12-53-44','Run-15-06-26-11-23-13','Run-15-07-31-18-30-14',
#               'Run-16-02-15-13-46-34','Run-16-02-29-11-54-20','Run-16-03-09-13-00-14',
#               'Run-16-03-22-18-09-33','Run-16-03-30-12-44-57','Run-16-04-12-11-54-27',
#               'Run-16-04-20-11-22-48','Run-16-05-05-14-08-52','Run-16-05-12-14-07-59',
#               'Run-16-05-17-14-40-34','Run-16-06-02-12-35-56','Run-16-06-17-12-09-12',
#               'Run-16-06-27-17-50-08','Run-16-07-06-18-25-19','Run-16-07-12-11-44-55',
#               'Run-16-07-18-11-50-24','Run-16-07-21-11-59-39','Run-16-07-28-12-49-17',
#               'Run-16-08-04-17-23-52','Run-16-08-09-00-29-54','Run-16-08-16-00-22-26']

    runDirs = ['Run-15-06-25-12-53-44']
#    runDirs = ['Run-15-06-26-11-23-13','Run-15-07-31-18-30-14']
#    runDirs = ['Run-15-08-18-14-51-18','Run-15-08-31-00-23-36','Run-15-09-21-20-58-01']
#    runDirs = ['Run-15-09-23-21-16-00','Run-15-10-03-09-26-22','Run-15-10-13-13-27-09']
#    runDirs = ['Run-15-10-21-13-12-27','Run-15-10-29-15-56-36','Run-15-11-09-11-30-13']
#    runDirs = ['Run-15-11-20-11-34-48','Run-15-11-24-15-35-32','Run-15-12-14-11-21-45']
#    runDirs = ['Run-15-12-26-08-30-40','Run-16-01-07-12-16-36','Run-16-02-02-16-26-26']
#    runDirs = ['Run-16-02-15-13-46-34','Run-16-02-29-11-54-20','Run-16-03-09-13-00-14']
#    runDirs = ['Run-16-03-22-18-09-33','Run-16-03-30-12-44-57','Run-16-04-12-11-54-27']
#    runDirs = ['Run-16-04-20-11-22-48','Run-16-05-05-14-08-52','Run-16-05-12-14-07-59']
#    runDirs = ['Run-16-05-17-14-40-34','Run-16-06-02-12-35-56','Run-16-06-17-12-09-12']
#    runDirs = ['Run-16-06-27-17-50-08','Run-16-07-06-18-25-19','Run-16-07-12-11-44-55']
#    runDirs = ['Run-16-07-18-11-50-24','Run-16-07-21-11-59-39','Run-16-07-28-12-49-17']
#    runDirs = ['Run-16-01-07-12-16-36']
#    runDirs = ['Run-16-08-04-17-23-52','Run-16-08-09-00-29-54','Run-16-08-16-00-22-26']
    for run in runDirs:
        main(['',mDir,run])
