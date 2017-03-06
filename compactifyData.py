#!/home/bjs66/anaconda2/bin/python

import h5py
import numpy as np
import os

dataKeys = ['timestamp','median-csi-baseline','average-csi-baseline','std-csi-baseline',
            'vanilla-pt-peaks','vanilla-roi-peaks','vanilla-iw-peaks','vanilla-arrival-index','vanilla-charge','vanilla-rt-10','vanilla-rt-50','vanilla-rt-90',
            'cmf-pt-peaks','cmf-roi-peaks','cmf-iw-peaks','cmf-arrival-index','cmf-charge','cmf-rt-10','cmf-rt-50','cmf-rt-90',
            'lbl-charge','lbl-rt-10','lbl-rt-50','lbl-rt-90']

def main(argv):
    mainDir = argv[1]
    run = argv[2]

    # Create/open stability HDF5 file that contains all stability data
    h5Out = h5py.File(mainDir + '/Metadata/%s-Final-Data.h5'%run,'w')

    # Determine all days in run folder that need to be analyzed
    h5Days = [x for x in np.sort(os.listdir(mainDir + run)) if '.h5' in x]

    # For each day get the times and the corresponding SPEQ fits
    for day in h5Days:

        # Show which dataset is currently being analyzed
        print run,day
        d = day.split('.')[0]

        # Open current hdf5 file
        h5In = h5py.File(mainDir + run + '/' + day, 'r')
        timeBins = h5In['/SPEQ/vanilla/Times'][...]
        timeBinsHumanReadable = np.sort(h5In['/I'].keys())
        for i in range(len(timeBins)):
            currentTimeGroup = h5Out.create_group('/%s/%s/%s'%(run,d,timeBinsHumanReadable[i]))
            for analysisType in ['vanilla','lbl','cmf']:
                currentTimeGroup.attrs['%s-spe-charge'%analysisType] = h5In['/SPEQ/%s/PolyaBest'%analysisType][i,0]

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
            numberOfTriggers = {'with-power': np.zeros(len(timeBins)), 'without-power': np.zeros(len(timeBins)),
                                'bad-power': np.zeros(len(timeBins)), 'total': np.zeros(len(timeBins))}
            if qSize == 0:
                qIdxUpdate = False

            # Add beam power to the proper time bins
            for t,p in zip(noEventsTimeStamps,noEventBeamPower):
                if qIdxUpdate:
                    if t >= timeBins[qIdx+1]:
                        qIdx += 1
                    if qIdx >= qSize:
                        qIdxUpdate = False
                numberOfTriggers['total'][qIdx] += 1
                if p > 0:
                    numberOfTriggers['with-power'][qIdx] += 1
                    powerPerBin[qIdx] += p
                elif p == 0:
                    numberOfTriggers['without-power'][qIdx] += 1
                else:
                    numberOfTriggers['bad-power'][qIdx] += 1

            eventTimeIndex= h5In['/%s/speQindex'%wd][...]
            eventBeamPower = h5In['/%s/beam-power'%wd][...]

            for qIdx,p in zip(eventTimeIndex,eventBeamPower):
                numberOfTriggers['total'][qIdx] += 1
                if p > 0:
                    numberOfTriggers['with-power'][qIdx] += 1
                    powerPerBin[qIdx] += p
                elif p == 0:
                    numberOfTriggers['without-power'][qIdx] += 1
                else:
                    numberOfTriggers['bad-power'][qIdx] += 1

            for i in range(len(timeBins)):
                currentTimeGroup = h5Out['/%s/%s/%s'%(run,d,timeBinsHumanReadable[i])]
                currentWindowGroup = currentTimeGroup.create_group('%s'%wd)
                currentWindowGroup.attrs.create('triggers-with-power', numberOfTriggers['with-power'][i], dtype=np.uint32)
                currentWindowGroup.attrs.create('triggers-without-power', numberOfTriggers['without-power'][i], dtype=np.uint32)
                currentWindowGroup.attrs.create('triggers-with-bad-power', numberOfTriggers['bad-power'][i], dtype=np.uint32)
                currentWindowGroup.attrs.create('total-triggers', numberOfTriggers['total'][i], dtype=np.uint32)
                currentWindowGroup.attrs.create('total-power', powerPerBin[i]/1.0e6/3600.0/60.0, dtype=np.float64)
                currentWindowGroup.attrs.create('average-baseline', np.average(h5In['/I/%s/averageBaseline'%(timeBinsHumanReadable[i])]),dtype=np.float)
                currentWindowGroup.attrs.create('linear-gates', np.sum(h5In['/I/%s/linearGateCounter'%(timeBinsHumanReadable[i])]),dtype=np.uint32)
                currentWindowGroup.attrs.create('overflows', np.sum(h5In['/I/%s/overflowCounter'%(timeBinsHumanReadable[i])]),dtype=np.uint32)
                currentWindowGroup.attrs.create('muon-vetos', np.sum(h5In['/I/%s/muonVetoCounter'%(timeBinsHumanReadable[i])]),dtype=np.uint32)
                currentWindowGroup.attrs.create('vanilla-pt-acceptance', (1.0*np.cumsum(h5In['/I/%s/peaksIn%s/vanilla/pt'%(timeBinsHumanReadable[i],wd)]) / np.sum(h5In['/I/%s/peaksIn%s/vanilla/pt'%(timeBinsHumanReadable[i],wd)])),dtype=np.float64)
                currentWindowGroup.attrs.create('cmf-pt-acceptance', (1.0*np.cumsum(h5In['/I/%s/peaksIn%s/cmf/pt'%(timeBinsHumanReadable[i],wd)])[:11]/np.sum(h5In['/I/%s/peaksIn%s/cmf/pt'%(timeBinsHumanReadable[i],wd)])),dtype=np.float64)

                cut_iw = np.array((h5In['/%s/cmf-iw-peaks'%wd][...] >= 6) + (h5In['/%s/vanilla-iw-peaks'%wd][...] >= 6),dtype=bool)
                cut_mv = (h5In['/%s/muon-veto-flag'%wd][...] == 0)
                cut_o = (h5In['/%s/overflow-flag'%wd][...] == 0)
                cut_lg = (h5In['/%s/linear-gate-flag'%wd][...] == 0)
                cut_qidx = (h5In['/%s/speQindex'%wd][...] == i)

                cut =  cut_iw * cut_mv * cut_o * cut_lg * cut_qidx
                for dK in dataKeys:
                    currentWindowGroup.create_dataset(dK,data=h5In['/%s/%s'%(wd,dK)][...][cut])

        h5In.close()
    h5Out.close()
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
