#!/usr/bin/env python

import h5py
import numpy as np
import os
import sys

dataKeys = ['timestamp','median-csi-baseline','average-csi-baseline','std-csi-baseline',
            'vanilla-pt-peaks','vanilla-roi-peaks','vanilla-iw-peaks','vanilla-arrival-index','vanilla-charge','vanilla-rt-10','vanilla-rt-50','vanilla-rt-90',
            'cmf-pt-peaks','cmf-roi-peaks','cmf-iw-peaks','cmf-arrival-index','cmf-charge','cmf-rt-10','cmf-rt-50','cmf-rt-90',
            'lbl-charge','lbl-rt-10','lbl-rt-50','lbl-rt-90','beam-power']

def main(argv):
    mainDir = argv[1]
    run = argv[2]

    # Define timezones used in analysis
    eastern = pytz.timezone('US/Eastern')
    utc = pytz.utc
    epochBeginning = utc.localize(datetime.datetime(1970,1,1))

    # Read times that shall be excluded from the analysis
    excludeTimes = np.loadtxt(excludeTimeFile,dtype=str)

    exTS = []
    for t in excludeTimes:
        exTS.append([(eastern.localize(datetime.datetime.strptime(x,'%Y-%m-%d-%H-%M-%S')).astimezone(utc)-epochBeginning).total_seconds() for x in t])


 
    # Create/open stability HDF5 file that contains all stability data
    h5Out = h5py.File(mainDir + '/Compactified/%s-Compactified.h5'%run,'w')

    # Determine all days in run folder that need to be analyzed
    h5Days = [x for x in np.sort(os.listdir(mainDir + run)) if '.h5' in x]

    # For each day get the times and the corresponding SPEQ fits
    for day in h5Days:
        d = day.split('.')[0]
        h5In = h5py.File(os.path.join(mainDir,run,day),'r')
        speqCharge = h5In['/SPEQ/lbl/PolyaBest'][...][:,0]

        for wd in ['S','B']:
            peaksInIW = h5In['/%s/vanilla-iw-peaks'%wd][...]
            peaksInPT = h5In['/%s/vanilla-pt-peaks'%wd][...]
            rt1090 = h5In['/%s/lbl-rt-90'%wd][...] - h5In['/%s/lbl-rt-10'%wd][...]
            rt050 = h5In['/%s/lbl-rt-50'%wd][...]
            charge = h5In['/%s/lbl-charge'%wd][...]
            speqIdx = h5In['/%s/speQindex'%wd][...]
            NPE = charge/speqCharge[speqIdx]
            arrivalIndex = h5In['/%s/vanilla-arrival-index'%wd][...]
            power = h5In['/%s/beam-power'%wd][...]
            overflow = h5In['/%s/overflow-flag'%wd][...]
            muonVeto = h5In['/%s/muon-veto-flag'%wd][...]
            linearGate = h5In['/%s/linear-gate-flag'%wd][...]
            
            NPE[np.isnan(NPE)] = -1

            cutIW = np.logical_or((peaksInIW >= 6),(NPE > 30))
            cutPT = peaksInPT <= 10
            cutPower = power > -0.9
            cutLinGate = linearGate == 0
            cutMuonVeto = muonVeto == 0
            cutNAN = NPE >= 0

            cutTotal = cutIW * cutPT * cutPower * cutLinGate * cutMuonVeto * cutNAN

            h5Out.create_dataset('/%s/%s/peaks-in-pt'%(d,wd), data=peaksInPT[cutTotal])
            h5Out.create_dataset('/%s/%s/peaks-in-iw'%(d,wd), data=peaksInIW[cutTotal])
            h5Out.create_dataset('/%s/%s/rt1090'%(d,wd), data=rt1090[cutTotal])
            h5Out.create_dataset('/%s/%s/rt050'%(d,wd), data=rt050[cutTotal])
            h5Out.create_dataset('/%s/%s/npe'%(d,wd), data=NPE[cutTotal])
            h5Out.create_dataset('/%s/%s/arrival'%(d,wd), data=arrivalIndex[cutTotal])
            h5Out.create_dataset('/%s/%s/power'%(d,wd), data=power[cutTotal])
            h5Out.create_dataset('/%s/%s/overflow'%(d,wd), data=overflow[cutTotal])
            
        h5In.close()
    h5Out.close()
# ============================================================================
#                                Run program
# ============================================================================
if __name__ == '__main__':
    main(sys.argv)
