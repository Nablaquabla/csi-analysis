import numpy as np
import h5py
import datetime
import pytz
import sys
import os
import easyfy as ez

def main(args):
    getMetadata = True
    # Define timezones used in analysis
    eastern = pytz.timezone('US/Eastern')
    utc = pytz.utc
    epochBeginning = utc.localize(datetime.datetime(1970,1,1))

    # Define analysis constants
    onsetIndex = {'S': 27475, 'B': 19950}

    # Prepare cuts
    dataDir = args[0]
    outDir = args[1]
    minPeaksInIW = args[2]
    maxPeaksInPT = args[3]

    arrivalMaxTime = 3000
    riseTime = {'RT1090': [args[4],args[5]], 'RT050': [args[6],args[7]]}
    npeMax = 30

    # Prepare data arrays to store final histograms
    npeBins = 40
    arrBins = 150

    # Find each data file and extract necessary info
    fileList = [x for x in np.sort(os.listdir('./')) if '.h5' in x]

    for fn in fileList:
        npeHist = {}
        arrHist = {}
        timeHist = {}
        timeArr = {}
        for aT in ['vanilla','lbl','cmf']:
            npeHist[aT] = {'on' : {'S': np.zeros(npeBins), 'B': np.zeros(npeBins)},
                           'off': {'S': np.zeros(npeBins), 'B': np.zeros(npeBins)}}
            arrHist[aT] = {'on' : {'S': np.zeros(arrBins), 'B': np.zeros(arrBins)},
                           'off': {'S': np.zeros(arrBins), 'B': np.zeros(arrBins)}}
            timeArr[aT] = {'on' : {'S': [], 'B': []},
                           'off': {'S': [], 'B': []}}
            timeHist[aT] = {'on' : {'S': [], 'B': []},
                            'off': {'S': [], 'B': []}}

        infoData = {'total-triggers': [],
                    'on-triggers': [],
                    'off-triggers': [],
                    'bad-triggers': [],
                    'cmf-spe-charge': [],
                    'vanilla-spe-charge': [],
                    'lbl-spe-charge': [],
                    'vanilla-pt-acceptance-b': [],
                    'vanilla-pt-acceptance-s': [],
                    'cmf-pt-acceptance-b': [],
                    'cmf-pt-acceptance-s': [],
                    'time': [],
                    'power': [],
                    'muon-vetos': [],
                    'linear-gates': [],
                    'overflows': []}

        # Open data file, get all days in run and iterate through them
        h5In = h5py.File('./%s'%fn,'r')
        dayList = np.sort(h5In.keys())

        for day in dayList:

            # Let me know what's currently being analyzed
            print fn, day

            # Get each 10 minute bin for each day and iterate through them
            timeList = np.sort(h5In['/%s'%day].keys())
            for time in timeList:

                # Create shortcut for the current hdf5 group /day/time
                cGrp = h5In['/%s/%s'%(day,time)]

                # Get all the info data for the current timestamp
                infoData['total-triggers'].append(cGrp['S'].attrs['total-triggers'])
                infoData['on-triggers'].append(cGrp['S'].attrs['triggers-with-power'])
                infoData['off-triggers'].append(cGrp['S'].attrs['triggers-without-power'])
                infoData['bad-triggers'].append(cGrp['S'].attrs['triggers-with-bad-power'])
                infoData['power'].append(cGrp['S'].attrs['total-power'])
                infoData['muon-vetos'].append(cGrp['S'].attrs['muon-vetos'])
                infoData['linear-gates'].append(cGrp['S'].attrs['linear-gates'])
                infoData['overflows'].append(cGrp['S'].attrs['overflows'])
                infoData['vanilla-spe-charge'].append(cGrp.attrs['vanilla-spe-charge'])
                infoData['lbl-spe-charge'].append(cGrp.attrs['lbl-spe-charge'])
                infoData['cmf-spe-charge'].append(cGrp.attrs['cmf-spe-charge'])
                infoData['cmf-pt-acceptance-b'].append((cGrp['B'].attrs['cmf-pt-acceptance'])[:11])
                infoData['cmf-pt-acceptance-s'].append((cGrp['S'].attrs['cmf-pt-acceptance'])[:11])
                infoData['vanilla-pt-acceptance-b'].append((cGrp['B'].attrs['vanilla-pt-acceptance'])[:11])
                infoData['vanilla-pt-acceptance-s'].append((cGrp['S'].attrs['vanilla-pt-acceptance'])[:11])
                infoData['time'].append(((eastern.localize(datetime.datetime.strptime(day+time,'%y%m%d%H%M%S'))).astimezone(utc) - epochBeginning).total_seconds())

                # Extract info for every analysis type available
                for aT in ['vanilla','lbl','cmf']:

                    # Extract info for both windows (B+S)
                    for wd in ['S', 'B']:

                        # Get SPE charge for the current analysis type and time bin
                        speq = cGrp.attrs['%s-spe-charge'%aT]

                        # Get the correct pretrace cut (lbl uses vanilla peaks for all cut purposes)
                        if aT == 'lbl':
                            cut_pt = (cGrp['%s/vanilla-pt-peaks'%(wd)][...] <= maxPeaksInPT )
                        else:
                            cut_pt = (cGrp['%s/%s-pt-peaks'%(wd,aT)][...] <= maxPeaksInPT )

                        # Get correct cut on arrival times for the NPE spectrum
                        if aT == 'lbl':
                            arrivalTime = cGrp['%s/vanilla-arrival-index'%(wd)][...] - onsetIndex[wd]
                        else:
                            arrivalTime = cGrp['%s/%s-arrival-index'%(wd,aT)][...] - onsetIndex[wd]
                        cut_arrival = (arrivalTime >= 0) * (arrivalTime <= arrivalMaxTime)

                        #  Get risetime cut
                        rt050 = cGrp['%s/%s-rt-50'%(wd,aT)][...]
                        cut_rt050 = (rt050 >= riseTime['RT050'][0]) * (rt050 <= riseTime['RT050'][1])
                        rt1090 = cGrp['%s/%s-rt-90'%(wd,aT)][...] - cGrp['%s/%s-rt-10'%(wd,aT)][...]
                        cut_rt1090 = (rt1090 >= riseTime['RT1090'][0]) * (rt1090 <= riseTime['RT1090'][1])

                        # Get correct cut on number of photoelectrons in integration window
                        npe = cGrp['%s/%s-charge'%(wd,aT)][...]/speq
                        cut_npe = (npe <= npeMax)

                        # Get cherenkov cut
                        if aT == 'lbl':
                            peaksInIW = cGrp['%s/vanilla-iw-peaks'%(wd)][...]
                        else:
                            peaksInIW = cGrp['%s/%s-iw-peaks'%(wd,aT)][...]
                        cut_iw = peaksInIW >= minPeaksInIW

                        # Get correct beam power cut
                        cut_bp = {}
                        cut_bp['on'] = (cGrp['%s/beam-power'%(wd)][...] > 0)
                        cut_bp['off'] = (cGrp['%s/beam-power'%(wd)][...] == 0)

                        # Split into beam on and off periods:
                        for bStatus in ['on','off']:

                            # Get energy/npe spectrum
                            cut = np.asarray(cut_pt * cut_arrival * cut_rt050 * cut_rt1090 * cut_iw * cut_bp[bStatus], dtype=bool)
                            _tHist = np.histogram(npe[cut],npeBins,[0,npeBins])[0]
                            if np.sum(_tHist > 0):
                                npeHist[aT][bStatus][wd] = np.vstack((npeHist[aT][bStatus][wd],_tHist))
                                timeHist[aT][bStatus][wd].append(((eastern.localize(datetime.datetime.strptime(day+time,'%y%m%d%H%M%S'))).astimezone(utc) - epochBeginning).total_seconds())

                            # Get arrival spectrum
                            cut = np.asarray(cut_pt * cut_npe * cut_rt050 * cut_rt1090 * cut_iw * cut_bp[bStatus], dtype=bool)
                            _tHist = np.histogram(arrivalTime[cut],arrBins,[0,7500])[0]
                            if np.sum(_tHist > 0):
                                arrHist[aT][bStatus][wd] = np.vstack((arrHist[aT][bStatus][wd],_tHist))
                                timeArr[aT][bStatus][wd].append(((eastern.localize(datetime.datetime.strptime(day+time,'%y%m%d%H%M%S'))).astimezone(utc) - epochBeginning).total_seconds())
        h5In.close()

        run = fn[:-14]
        # Save spectra to file
        newpath = './Processed/PIW-%d/PPT-%d'%(minPeaksInIW,maxPeaksInPT)
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        h5Out = h5py.File('./Processed/PIW-%d/PPT-%d/%s-Spectra.h5'%(minPeaksInIW,maxPeaksInPT,run),'w')
        for aT in ['vanilla','lbl','cmf']:
            for bP in ['on','off']:
                for wd in ['S','B']:
                    if len(timeHist[aT][bP][wd]) > 0:
                        h5Out.create_dataset('/%s/%s/%s/npe/histogram'%(aT,bP,wd),data=npeHist[aT][bP][wd][1:],dtype=np.uint16)
                        h5Out.create_dataset('/%s/%s/%s/npe/time'%(aT,bP,wd),data=timeHist[aT][bP][wd],dtype=np.uint64)
                    if len(timeArr[aT][bP][wd]) > 0:
                        h5Out.create_dataset('/%s/%s/%s/arrival/histogram'%(aT,bP,wd),data=arrHist[aT][bP][wd][1:],dtype=np.uint16)
                        h5Out.create_dataset('/%s/%s/%s/arrival/time'%(aT,bP,wd),data=timeArr[aT][bP][wd],dtype=np.uint64)
        h5Out.close()

        if getMetadata:
            h5Out = h5py.File('./Processed/%s-Metadata.h5'%run,'w')
            for tType in ['total','on','off','bad']:
                h5Out.create_dataset('%s-triggers'%tType,data=infoData['%s-triggers'%tType],dtype=np.uint32)
            for tType in ['muon-vetos','linear-gates','overflows']:
                h5Out.create_dataset('%s'%tType,data=infoData['%s'%tType],dtype=np.uint32)
            for aT in ['vanilla','cmf']:
                h5Out.create_dataset('%s-pt-acceptance-s'%aT,data=infoData['%s-pt-acceptance-s'%aT],dtype=np.float)
                h5Out.create_dataset('%s-pt-acceptance-b'%aT,data=infoData['%s-pt-acceptance-b'%aT],dtype=np.float)
            for aT in ['vanilla','cmf','lbl']:
                h5Out.create_dataset('%s-spe-charge'%aT,data=infoData['%s-spe-charge'%aT],dtype=np.float)
            h5Out.create_dataset('power',data=infoData['power'],dtype=np.float64)
            h5Out.create_dataset('time',data=infoData['time'],dtype=np.uint64)
            h5Out.close()

if __name__ == '__main__':
    dataDir = sys.argv[1]
    outDir = sys.argv[2]
    piw = int(sys.argv[3])
    ppt = int(sys.argv[4])
    minRT050 = int(sys.argv[5])
    maxRT050 = int(sys.argv[6])
    minRT1090 = int(sys.argv[7])
    maxRT1090 = int(sys.argv[8])
    main(np.asarray(sys.argv[1:],dtype=np.int))


