#!/home/bjs66/anaconda2/bin/python
"""
Created on Mon Feb 01 15:03:56 2016

@author: Nablaquabla
"""
import h5py
import numpy as np
import easyfit as ef
import sys
import os
import datetime
import pytz

# Define timezones used in analysis
eastern = pytz.timezone('US/Eastern')
utc = pytz.utc
epochBeginning = utc.localize(datetime.datetime(1970,1,1))

#=============================================================================#
#                           Define fit functions
#=============================================================================#
# Single Polya and flat offset
def polya(x,q,t,m):
    return (1.0*x/q)**(m*(t+1.0)-1.0) * np.exp(-(t+1.0)*x/q) / (np.exp(-(t+1.0)))

def gauss(x,q,s,m):
    return np.exp(-0.5*((x-m*q)/s)**2/m)

def gFit(x,p):
    _t1 = p[2] * gauss(x,p[0],p[1],1)
    _tbg = p[3] * np.exp(-x/p[4])
    return _t1 + _tbg

def pFit(x,p):
    _t1 = p[2] * polya(x,p[0],p[1],1)
    _tbg = p[3] * np.exp(-x/p[4])
    return _t1 + _tbg

def gFit3(x,p):
    _t1 = p[2] * gauss(x,p[0],p[1],1)
    _t2 = p[3] * gauss(x,p[0],p[1],2)
    _t3 = p[4] * gauss(x,p[0],p[1],3)
    _tn = p[5] * np.exp(-x/p[6])
    return (_t1 + _t2 + _t3 + _tn) /( 1.0 + np.exp(- p[7] * (x - p[8]))) + p[9]

def pFit3(x,p):
    _t1 = p[2] * polya(x,p[0],p[1],1)
    _t2 = p[3] * polya(x,p[0],p[1],2)
    _t3 = p[4] * polya(x,p[0],p[1],3)
    _tn = p[5] * np.exp(-x/p[6])
    return (_t1 + _t2 + _t3 + _tn) /( 1.0 + np.exp(- p[7] * (x - p[8])))

# ============================================================================
#                                Run program
# ============================================================================
def main(args):
    mainDir = args[1]
    run = args[2]

    # Declare main and run dirs
    runDir = mainDir + run

    # Get all days in given run folder
    daysInRun = [x.split('.')[0] for x in os.listdir(runDir) if 'h5' in x]

    # Create dummy pars variables
    pars = np.zeros((3,10))

    # For each day in the run folder read the HDF5 file and fit SPEQ spectra
    for day in daysInRun:
        h5In = h5py.File(runDir + '/' + day + '.h5', 'r+')

#        for analysisType in ['lbl','vanilla','cmf']:
        for analysisType in ['vanilla','lbl','cmf']:
#        for analysisType in ['cmf','vanilla','lbl']:

            # Prepare/reset output array
            speQArr = {'Times': [],
                       'PolyaBest': [],
                       'PolyaErr': []}

            # Perform analysis for each hour in day file
            for time in np.sort(h5In['/I/'].keys()):

                # Calculate seconds in epoch based on day and hour
                eTS = eastern.localize(datetime.datetime.strptime(day+time,'%y%m%d%H%M%S'))
                uTS = eTS.astimezone(utc)
                sSE = (uTS - epochBeginning).total_seconds()

                speQArr['Times'].append(sSE)

                # Prepare fit data
                xQ = np.arange(-50,250)
                yQ = h5In['/I/%s/peakCharge/%s'%(time,analysisType)][...]

                # If not enough SPE have been found use previous data point
                if np.sum(yQ) > 1e3:
                    # Scaling to help preventing overflows
                    scaling = 1.0
                    yf = yQ/6.0

                    # Data arrays used for bad fit rejection
                    x2 = 1000.0
                    x2Arr = []
                    pArr = []

                    # Prevent fit from exploring negative numbers
                    xMin = xQ[np.argmax(yf > 20)]
                    c = (xQ >= xMin)

                    p0 = [70.0, 6.0, 500, 10, 0.002, 5e4, 10.0, 0.5 , 17.0]
                    lims = [[0,1,1,50,100],[1,1,1,4.75,6.75],[2,1,0,0,0],[3,1,1,0,40],[4,1,1,0,0.3],[5,1,0,0,0],[7,1,1,0,20],[8,1,1,10,25]]

                    # Fit data - If a bad fit is encountered, adjust parameters and refit
                    while x2 > 0.55*scaling:
                        _,pars,xfit,yfit = ef.arbFit(pFit3,xQ[c],yf[c],'Poisson',p0,lims)
                        x2 = np.sum((pFit3(xQ[c],pars[0]) - yf[c])**2/pFit3(xQ[c],pars[0]))/np.sum(c)
                        x2Arr.append(x2)
                        pArr.append(pars)
                        if x2 < 0.5*scaling and pars[0][1] != 4:
                            break
                        if len(x2Arr) > 20:
                            iMin = np.argmin(x2Arr)
                            pars = pArr[iMin]
                            break
                        print time
                        p0[7] += 0.1*(0.5-np.random.rand())
                        p0[8] += (0.5-np.random.rand())

                    speQArr['PolyaBest'].append(pars[0][:])
                    speQArr['PolyaErr'].append(pars[2][:])

                else:
                    speQArr['PolyaBest'].append(pars[0][:])
                    speQArr['PolyaErr'].append(pars[2][:])

            # Write data to HDF5 file replacing already existing data
            for key in speQArr.keys():
                if '/SPEQ/%s/%s'%(analysisType,key) in h5In:
                    del h5In['/SPEQ/%s/%s'%(analysisType,key)]
                h5In.create_dataset('/SPEQ/%s/%s'%(analysisType,key),data=speQArr[key])

        h5In.close()
# ============================================================================
#                                Run program
# ============================================================================
if __name__ == '__main__':
    main(sys.argv)
















