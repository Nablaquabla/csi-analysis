import numpy as np
import h5py
import datetime
import pytz
import sys
import os
import easyfy as ez

def main(args):

    # Read output and data dirs
    dataDir = args[0]
    run = args[1]
    outDir = args[2]

    # Define SPEQ type to be analyzed (lbl,vanilla,cmf)
    speqType = 'lbl'

    # Define timezones used in analysis
    eastern = pytz.timezone('US/Eastern')
    utc = pytz.utc
    epochBeginning = utc.localize(datetime.datetime(1970,1,1))

    # Read times that shall be excluded from the analysis
    excludeTimes = np.loadtxt('excludeTimes.dat',dtype=str)

    exTS = []
    for t in excludeTimes:
        exTS.append([(eastern.localize(datetime.datetime.strptime(x,'%Y-%m-%d-%H-%M-%S')).astimezone(utc)-epochBeginning).total_seconds() for x in t])


    # Define analysis constants
    onsetIndex = {'S': 27475, 'B': 19950}

    # Define which cuts are being analyzed
    maxPEPTArr = np.arange(11)
    minPEIWArr = [6,7,8]
    minRT050Arr = [0,25,50,75,100]
    maxRT050Arr = [750,1000,1250,1500]
    minRT1090Arr = [0,125,250,375,500]
    maxRT1090Arr = [1125,1250,1375,1500]
#    maxPEPTArr = [10]
#    minPEIWArr = [3]
#    minRT050Arr = [100]
#    maxRT050Arr = [750]
#    minRT1090Arr = [500]
#    maxRT1090Arr = [1125]

    # Define maximum arrival time of an event that shall be added to the NPE histogram
    # as well as the maximum NPE of an event that shall be added to the arrival histogram
    arrivalMaxTime = 3000
    npeMax = 30

    # Prepare data arrays to store final histograms
    nBins = {'NPE': 80, 'Arrival': 150}

    # Get all runs in the Processed folder
#    runList = [x for x in np.sort(os.listdir(dataDir)) if 'Run' in x]
    runList = [run]

    # For each run go through all days and get a single histogram
    # but exclude all dates as listed in the exclusion file
    for run in runList:

        infoData = {'bad-triggers': 0, 'on-triggers': 0, 'off-triggers': 0, 'power': 0, }

        # Setup data array that stores the full run information
        data = {}
        for dt in ['NPE','Arrival']:
            data[dt] = {}
            for minPEIW in minPEIWArr:
                data[dt][minPEIW] = {}
                for maxPEPT in maxPEPTArr:
                    data[dt][minPEIW][maxPEPT] = {}
                    for minRT050 in minRT050Arr:
                        data[dt][minPEIW][maxPEPT][minRT050] = {}
                        for maxRT050 in maxRT050Arr:
                            data[dt][minPEIW][maxPEPT][minRT050][maxRT050] = {}
                            for minRT1090 in minRT1090Arr:
                                data[dt][minPEIW][maxPEPT][minRT050][maxRT050][minRT1090] = {}
                                for maxRT1090 in maxRT1090Arr:
                                    data[dt][minPEIW][maxPEPT][minRT050][maxRT050][minRT1090][maxRT1090] = {}
                                    for wd in ['S','B']:
                                        data[dt][minPEIW][maxPEPT][minRT050][maxRT050][minRT1090][maxRT1090][wd] = {}
                                        for bstatus in ['on','off']:
                                            data[dt][minPEIW][maxPEPT][minRT050][maxRT050][minRT1090][maxRT1090][wd][bstatus] = np.zeros(nBins[dt])

        # Determine all day hdf5 files and iterate through them
        dayList = np.sort([x for x in os.listdir(os.path.join(dataDir,run)) if '.h5' in x])
        for day in dayList:

            # Open current day file in read only mode! All results will be added to the output file
            h5In = h5py.File(os.path.join(dataDir,run,day),'r')

            # Get time and spe charges of current day
            speCharges = {}
            speCharges['time'] = h5In['/SPEQ/%s/Times'%speqType][...]
            speCharges['polya'] = h5In['/SPEQ/%s/PolyaBest'%speqType][...][:,0]

            # Get temporary speqtype. lbl uses vanilla for PE identification etc.
            if speqType == 'cmf':
                _tST = 'cmf'
            else:
                _tST = 'vanilla'

            # For both signal and background windows calculate the spectra, where data is split into
            # beam on and off periods for both signal and background regions.
            for wd in ['S','B']:

                # Analyze no event data
                noEventTimestamps = h5In['/%s/no-event'%wd][...]
                noEventPower = h5In['/%s/no-event-beam-power'%wd][...]
                timeExclusionCut = np.zeros(len(noEventTimestamps))
                for t in exTS:
                    timeExclusionCut = timeExclusionCut + np.asarray((noEventTimestamps >= t[0]) * (noEventTimestamps <= t[1]),dtype=int)
                timeExclusionCut = np.logical_not(np.asarray(timeExclusionCut,dtype=bool))

                currentPower = noEventPower[timeExclusionCut]
                beamOn = (currentPower > 10)
                beamOff = (currentPower <= 10) * (currentPower >= -0.1)
                beamBad = (currentPower == -1)
                infoData['on-triggers'] = infoData['on-triggers'] + np.sum(beamOn)
                infoData['off-triggers'] = infoData['off-triggers'] + np.sum(beamOff)
                infoData['bad-triggers'] = infoData['bad-triggers'] + np.sum(beamBad)

                infoData['power'] = infoData['power'] + np.sum(currentPower[beamOn])/1.0e6/3600.0/60.0

                # Read all necessary data from file
                linGateFlag = h5In['/%s/linear-gate-flag'%wd][...]
                overflowFlag = h5In['/%s/overflow-flag'%wd][...]
                muonFlag = h5In['/%s/muon-veto-flag'%wd][...]

                # Cut all events with a linear gate, overflow or muon veto
                cutFlags = (linGateFlag == 0) * (overflowFlag == 0) * (muonFlag == 0)

                peInPT = h5In['/%s/%s-pt-peaks'%(wd,_tST)][...]
                peInIW = h5In['/%s/%s-iw-peaks'%(wd,_tST)][...]

                # Get risetimes
                rt1090 = h5In['/%s/%s-rt-90'%(wd,_tST)][...] - h5In['/%s/%s-rt-10'%(wd,_tST)][...]
                rt050 = h5In['/%s/%s-rt-50'%(wd,_tST)][...]

                # Get arrival times
                arrival = h5In['/%s/%s-arrival-index'%(wd,_tST)][...] - onsetIndex[wd]

                # Used for energy spectra
                charge = h5In['/%s/%s-charge'%(wd,speqType)][...]
                speWindow = h5In['/%s/speQindex'%wd][...]

                # Beam power for each event
                power = h5In['/%s/beam-power'%wd][...]

                # Get timestamps
                timestamps = h5In['/%s/timestamp'%wd][...]

                # Cycle through all different times for which we have different SPE charges
                for i in range(len(speCharges['time'])):

                    # Determine which data actually was taken in those charge windows
                    cutTime = (speWindow == i)

                    # Remove data that happens within any excluded time window
                    currentTimestamps = timestamps[cutTime]
                    timeExclusionCut = np.zeros(len(currentTimestamps))
                    for t in exTS:
                        timeExclusionCut = timeExclusionCut + np.asarray((currentTimestamps >= t[0]) * (currentTimestamps <= t[1]),dtype=int)
                    timeExclusionCut = np.logical_not(np.asarray(timeExclusionCut,dtype=bool))

                    if np.sum(timeExclusionCut) == 0:
                        continue
                    else:
                        # Convert charge subset to NPE
                        currentNPEPolya = charge[cutTime][timeExclusionCut]/speCharges['polya'][i]

                        # Get current arrival times
                        currentArrival = arrival[cutTime][timeExclusionCut]

                        # Separate the data that is necessary from the other data arrays
                        currentPeInPT = peInPT[cutTime][timeExclusionCut]
                        currentPeInIW = peInIW[cutTime][timeExclusionCut]
                        currentRt1090 = rt1090[cutTime][timeExclusionCut]
                        currentRt050 = rt050[cutTime][timeExclusionCut]
                        currentFlags = cutFlags[cutTime][timeExclusionCut]

                        currentPower = power[cutTime][timeExclusionCut]
                        beamOn = (currentPower > 10)
                        beamOff = (currentPower <= 10) * (currentPower >= -0.1)
                        beamBad = (currentPower == -1)

                        infoData['on-triggers'] = infoData['on-triggers'] + np.sum(beamOn)
                        infoData['off-triggers'] = infoData['off-triggers'] + np.sum(beamOff)
                        infoData['bad-triggers'] = infoData['bad-triggers'] + np.sum(beamBad)

                        infoData['power'] = infoData['power'] + np.sum(currentPower[beamOn])/1.0e6/3600.0/60.0

                        # Only add events with less than npeMax photoelectrons to the arrival spectrum
                        cutNPEForArrivalSpectrum = currentNPEPolya <= npeMax

                        # Only add events with an arrival time of less than arrivalMaxTime to the NPE spectrum
                        cutArrivalForNPESpectrum = currentArrival <= arrivalMaxTime

                        # Cut everything with less than minPEIW peaks in the integration window
                        # and less than 20 total PE from charge integration
                        cutCherenkov = np.logical_or((currentPeInIW >= minPEIW),(currentNPEPolya >= 20))

                        # Cut everything above diagonal in 2d risetime plot as it represents misidentified onsets
                        cutRTBasic = currentRt050 < currentRt1090

                        for minPEIW in minPEIWArr:
                            cutCherenkov = (currentPeInIW >= minPEIW)

                            for maxPEPT in maxPEPTArr:
                                cutMaxPEPT = (currentPeInPT <= maxPEPT)

                                for minRT050 in minRT050Arr:
                                    cutMinRT050 = currentRt050 >= minRT050

                                    for maxRT050 in maxRT050Arr:
                                        cutMaxRT050 = currentRt050 <= maxRT050

                                        for minRT1090 in minRT1090Arr:
                                            cutMinRT1090 = currentRt1090 >= minRT1090

                                            for maxRT1090 in maxRT1090Arr:
                                                cutMaxRT1090 = currentRt1090 <= maxRT1090

                                                cutTotal = cutCherenkov * cutMaxPEPT * cutMinRT050 * cutMaxRT050 * cutMinRT1090 * cutMaxRT1090 * cutRTBasic * currentFlags
                                                cutForNPE = cutTotal * cutArrivalForNPESpectrum
                                                cutForArrival = cutTotal * cutNPEForArrivalSpectrum

                                                data['NPE'][minPEIW][maxPEPT][minRT050][maxRT050][minRT1090][maxRT1090][wd]['on'] = data['NPE'][minPEIW][maxPEPT][minRT050][maxRT050][minRT1090][maxRT1090][wd]['on'] + np.histogram(currentNPEPolya[cutForNPE*beamOn],nBins['NPE'],[0,40])[0]
                                                data['Arrival'][minPEIW][maxPEPT][minRT050][maxRT050][minRT1090][maxRT1090][wd]['on'] = data['Arrival'][minPEIW][maxPEPT][minRT050][maxRT050][minRT1090][maxRT1090][wd]['on'] + np.histogram(currentArrival[cutForArrival*beamOn],nBins['Arrival'],[0,7500])[0]

                                                data['NPE'][minPEIW][maxPEPT][minRT050][maxRT050][minRT1090][maxRT1090][wd]['off'] = data['NPE'][minPEIW][maxPEPT][minRT050][maxRT050][minRT1090][maxRT1090][wd]['off'] + np.histogram(currentNPEPolya[cutForNPE*beamOff],nBins['NPE'],[0,40])[0]
                                                data['Arrival'][minPEIW][maxPEPT][minRT050][maxRT050][minRT1090][maxRT1090][wd]['off'] = data['Arrival'][minPEIW][maxPEPT][minRT050][maxRT050][minRT1090][maxRT1090][wd]['off'] + np.histogram(currentArrival[cutForArrival*beamOff],nBins['Arrival'],[0,7500])[0]
            h5In.close()

        fOut = h5py.File(outDir +'%s-Spectra.h5'%run,'w')
        for key in infoData.keys():
            fOut.attrs[key] = infoData[key]
        for dt in ['NPE','Arrival']:
            for minPEIW in minPEIWArr:
                for maxPEPT in maxPEPTArr:
                    for minRT050 in minRT050Arr:
                        for maxRT050 in maxRT050Arr:
                            for minRT1090 in minRT1090Arr:
                                for maxRT1090 in maxRT1090Arr:
                                    for wd in ['S','B']:
                                        for bStatus in ['on','off']:
                                            h5key = '/%s/%d/%d/%d/%d/%d/%d/%s/%s'%(dt,minPEIW,maxPEPT,minRT050,maxRT050,minRT1090,maxRT1090,wd,bStatus)
                                            fOut.create_dataset(h5key,data=data[dt][minPEIW][maxPEPT][minRT050][maxRT050][minRT1090][maxRT1090][wd][bStatus])
        fOut.close()

if __name__ == '__main__':
#    dataDir = sys.argv[1]
#    outDir = sys.argv[2]
    dataDir = 'F:/Work-Data-Storage/CsI/Condor/SNS/Testdir/Test-Data/'
    outDir = 'F:/Work-Data-Storage/CsI/Condor/SNS/Testdir/Output-Data/'
    main([dataDir,outDir])


