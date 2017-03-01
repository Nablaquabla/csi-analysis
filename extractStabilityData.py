#!/home/bjs66/anaconda2/bin/python

import h5py
import numpy as np
import os

def main(argv):
    mainDir = argv[1]
    run = argv[2]

    # Create/open stability HDF5 file that contains all stability data
    h5Stability = h5py.File(mainDir + '/Metadata/Stability.h5','a')

    # Determine all days in run folder that need to be analyzed
    h5Days = [x for x in os.listdir(mainDir + run) if '.h5' in x]

    # For each day get the times and the corresponding SPEQ fits
    for d in h5Days:
        f = h5py.File(mainDir + run + '/' + d, 'r')

        h5key = '/speq-fits/%s/%s/'%(run,d)
        if h5key in f:
            del f[h5key]
        h5Stability.create_dataset(h5key + 'time', data=f['/SPEQ/vanilla/Times'][...])
        h5Stability.create_dataset(h5key + 'vanilla/fit', data=f['/SPEQ/vanilla/PolyaBest'][...])
        h5Stability.create_dataset(h5key + 'vanilla/error', data=f['/SPEQ/vanilla/PolyaErr'][...])
        h5Stability.create_dataset(h5key + 'lbl/fit', data=f['/SPEQ/lbl/PolyaBest'][...])
        h5Stability.create_dataset(h5key + 'lbl/error', data=f['/SPEQ/lbl/PolyaErr'][...])
        h5Stability.create_dataset(h5key + 'cmf/fit', data=f['/SPEQ/cmf/PolyaBest'][...])
        h5Stability.create_dataset(h5key + 'cmf/error', data=f['/SPEQ/cmf/PolyaErr'][...])
        f.close()
    h5Stability.close()

# ============================================================================
#                                Run program
# ============================================================================
if __name__ == '__main__':
    mDir = '/home/bjs66/csi/bjs-analysis/'
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
