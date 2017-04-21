#!/usr/bin/env python
import os
import h5py
import numpy as np
import matplotlib.pylab as plt
import sys

def acceptance(x,p):
    return p[0]/(1.0+np.exp(-p[1]*(x-p[2]))) + p[3]*x

def main(minPEinIW):

    # Analysis options
    dataDir = '/data2/coherent/data/csi/bjs-analysis/Processed/Analyzed'
    outputDir = '/data2/coherent/data/csi/bjs-analysis/Processed/Analyzed'
    workingDir = '/nfs_home/bjo/GitHub/csi-analysis'
    nBins = {'NPE': 80, 'Arrival': 150}

    # Acceptances from stability analysis
    muonVetoAcceptance = (1.0 - 0.01095)
    overflowAcceptance = (1.0 - 0.00315)
    linGateAcceptance = (1.0 - 0.00809)
    pretraceAcceptance = np.array([0.16297553,0.39798555,0.59975277,0.7339427,0.81404367,0.86115311,0.890018,0.90886719,0.92199794,0.93164581])

    # Read uncut simulated spectra
    uncutNPE = np.loadtxt(os.path.join(workingDir,'Uncut-Signal-NPE-1GWHr.dat'))
    uncutArr = np.loadtxt(os.path.join(workingDir,'Uncut-Signal-Arrival-1GWHr.dat'))

    xSimNPE = np.mean(np.reshape(uncutNPE[0],(15,2)),axis=1)
    xSimArr = np.mean(np.reshape(uncutArr[0],(30,5)),axis=1)/1000.0

    minPEIWArr = [minPEinIW]
    peaksInPTArr = np.arange(10)
    minRT050Arr = [0,25,50,75,100]
    maxRT050Arr = [750,1000,1250,1500]
    minRT1090Arr = [0,125,250,375,500]
    maxRT1090Arr = [1125,1250,1375,1500]

    fOut = h5py.File(os.path.join(outputDir,'Data-Cuts-FOM-%d.h5'%minPEinIW),'w')
    for peaksInIW in minPEIWArr:
        for peaksInPT in peaksInPTArr:
            print peaksInIW, peaksInPT
            for minRT050 in minRT050Arr:
                for maxRT050 in maxRT050Arr:
                    for minRT1090 in minRT1090Arr:
                        for maxRT1090 in maxRT1090Arr:
                            infoData = {'on-triggers': 0, 'off-triggers': 0, 'bad-triggers': 0, 'power': 0}
                            spectra = {'NPE': {'on': {'S': np.zeros(nBins['NPE']), 'B': np.zeros(nBins['NPE'])},
                                               'off':  {'S': np.zeros(nBins['NPE']), 'B': np.zeros(nBins['NPE'])}},
                                       'Arrival': {'on': {'S': np.zeros(nBins['Arrival']), 'B': np.zeros(nBins['Arrival'])},
                                                   'off':  {'S': np.zeros(nBins['Arrival']), 'B': np.zeros(nBins['Arrival'])}}}
                            h5OutKey = '/Binning-40/PIW-%d-PPT-%d-RT50-%d-%d-RT1090-%d-%d'%(peaksInIW,peaksInPT,minRT050,maxRT050,minRT1090,maxRT1090)

                            # Read acceptances
                            fAcceptance = h5py.File(os.path.join(dataDir,'Acceptances.h5'),'r')
                            accPars = fAcceptance['/Binning-40/PIW-%d-PPT-%d-RT50-%d-%d-RT1090-%d-%d'%(peaksInIW,5,minRT050,maxRT050,minRT1090,maxRT1090)][...][0]
                            fAcceptance.close()

                            # Apply acceptances from Ba calibration to simulated signal spectra
                            yNPEMP = np.sum(np.reshape(uncutNPE[1]*acceptance(uncutNPE[0],accPars),(15,2)),axis=1)
                            yNPEMD= np.sum(np.reshape(uncutNPE[2]*acceptance(uncutNPE[0],accPars),(15,2)),axis=1)
                            yNPEED = np.sum(np.reshape(uncutNPE[3]*acceptance(uncutNPE[0],accPars),(15,2)),axis=1)
                            ySimNPE = (yNPEMP + yNPEMD + yNPEED)

                            yArrMP = np.sum(np.reshape(uncutArr[1],(30,5)),axis=1) * np.sum(uncutNPE[1]*acceptance(uncutNPE[0],accPars))/np.sum(uncutNPE[1])
                            yArrMD = np.sum(np.reshape(uncutArr[2],(30,5)),axis=1) * np.sum(uncutNPE[2]*acceptance(uncutNPE[0],accPars))/np.sum(uncutNPE[2])
                            yArrED = np.sum(np.reshape(uncutArr[3],(30,5)),axis=1) * np.sum(uncutNPE[3]*acceptance(uncutNPE[0],accPars))/np.sum(uncutNPE[3])
                            ySimArr = yArrMP + yArrMD + yArrED

                            # Read experimental data for each run and add to spectra
                            runList = np.sort([x for x in os.listdir(dataDir) if 'Run' in x])
                            for run in runList:
                                fIn = h5py.File(os.path.join(dataDir,run),'r')
                                for key in infoData.keys():
                                    infoData[key] = infoData[key] + fIn.attrs[key]

                                for tp in ['Arrival','NPE']:
                                    for bStatus in ['on']:
                                        for wd in ['B']:
                                            h5key = '/%s/%s/%s/%s/%s/%s/%s/%s/%s'%(tp,peaksInIW,peaksInPT,minRT050,maxRT050,minRT1090,maxRT1090,wd,bStatus)
                                            spectra[tp][bStatus][wd] = spectra[tp][bStatus][wd] + fIn[h5key][...]
                                fIn.close()


                            # Get proper scaling for the simulated spectra
                            npeScaling = muonVetoAcceptance * overflowAcceptance * linGateAcceptance * pretraceAcceptance[peaksInPT] * infoData['power']/2.0/1000.0
                            arrivalScaling = muonVetoAcceptance * overflowAcceptance * linGateAcceptance * pretraceAcceptance[peaksInPT] * infoData['power']/2.0/1000.0
                            ySimNPE = ySimNPE * npeScaling
                            ySimArr = ySimArr * arrivalScaling
                            # Get background data for beam on periods and estimate a FOM for how significant the signal will be above BG
                            beamStatus = 'on'

                            reshapeSizeNPE = (20,4)
                            xExpNPE = np.mean(np.reshape(np.arange(0,40,0.5)+0.25,reshapeSizeNPE),axis=1)
                            yExpNPEErr = np.sqrt(2.0*np.sum(np.reshape(spectra['NPE'][beamStatus]['B'],reshapeSizeNPE),axis=1))
                            yExpNPEErr[yExpNPEErr == 0] = 1


                            chi2NPE = 0
                            iStart = np.argmax(xExpNPE == xSimNPE[0])
                            for iSim in range(len(ySimNPE)):
                                iExp = iStart + iSim
                                chi2NPE = chi2NPE + (ySimNPE[iSim]/yExpNPEErr[iExp])**2

                            reshapeSizeArrival = (30,5)
                            xExpArr = np.mean(np.reshape(np.arange(0,15.0,0.1)+0.05,reshapeSizeArrival),axis=1)
                            yExpArrErr = np.sqrt(2.0*np.sum(np.reshape(spectra['Arrival'][beamStatus]['B'],reshapeSizeArrival),axis=1))
                            yExpArrErr[yExpArrErr == 0] = 1

                            chi2Arr = 0
                            iStart = np.argmax(xExpArr == xSimArr[0])
                            for iSim in range(len(ySimNPE)):
                                iExp = iStart + iSim
                                chi2Arr = chi2Arr + (ySimArr[iSim]/yExpArrErr[iExp])**2

                            fOut.create_dataset(h5OutKey, data=[chi2NPE, chi2Arr])
    fOut.close()
if __name__ == '__main__':
    minPEinIW = sys.argv[1]
    main(int(minPEinIW))
