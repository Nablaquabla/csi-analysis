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

dataType = 'Ba'

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
    day = args[3]

    # Declare main and run dirs
    runDir = mainDir + run

    # Create dummy pars variables
    pars = np.zeros((3,9))

    # For the given day read the HDF5 file and fit SPEQ spectra
    h5In = h5py.File(runDir + '/' + day + '.h5', 'r+')

    # Delete old fit data
    for analysisType in ['vanilla','lbl','cmf']:
        for key in ['Times','PolyaBest','PolyaErr','Chi2']:
            if '/SPEQ/%s/%s'%(analysisType,key) in h5In:
                del h5In['/SPEQ/%s/%s'%(analysisType,key)]

    # Analyze all available SPEQ distribution types
    for analysisType in ['vanilla','lbl','cmf']:

#    for analysisType in ['cmf']:

        # Prepare/reset output array
        speQArr = {'Times': [],
                   'PolyaBest': [],
                   'PolyaErr': [],
                   'Chi2': []}

        # Perform analysis for each hour in day file
        for time in np.sort(h5In['/I'].keys())[:]:

#            print analysisType,time
            # Calculate seconds in epoch based on day and hour
            eTS = eastern.localize(datetime.datetime.strptime(day+time,'%y%m%d%H%M%S'))
            uTS = eTS.astimezone(utc)
            sSE = (uTS - epochBeginning).total_seconds()
            speQArr['Times'].append(sSE)

            # Prepare fit data
            xQ = np.arange(-50,250)
            yQ = h5In['/I/%s/peakCharge/%s'%(time,analysisType)][...]

            # If not enough SPE have been found use previous data point
            if np.sum(yQ) > 1e3 and np.max(yQ) < 12500:

                # Scaling to help preventing overflows
                scaling = 1.0
                yf = yQ/6.0

                # Data arrays used for bad fit rejection
                fitWidth = 100.0
                x2 = 1000.0
                x2Arr = []
                pArr = []

                # Prevent fit from exploring negative numbers
                xMin = xQ[np.argmax(yf > 100)]
                if xMin < 12: xMin =12
                c = (xQ >= xMin)

                # Prepare initial fit parameter estimates and set fit limits
                if dataType == 'SNS':
                    if analysisType == 'cmf':
                        p0 = [70.0, 6.0, np.max(yf), np.max(yf)/50.0, 0.002, 5e4, 10.0, 0.5 , 17.0]
                        widthMinimum = 4.5
                        lims = [[0,1,1,50,100],[1,1,1,widthMinimum,6.75],[2,1,0,0,0],[3,1,1,0,100],[4,1,1,0,0.3],[5,1,1,0,1e6],[6,1,1,1,10],[7,1,1,0.225,0.55],[8,1,1,16,35]]

                    elif analysisType == 'vanilla':
                        p0 = [70.0, 6.0, np.max(yf), np.max(yf)/50.0, 0.002, 5e4, 10.0, 0.5 , 17.0]
                        widthMinimum = 4.75
                        lims = [[0,1,1,50,100],[1,1,1,widthMinimum,6.75],[2,1,0,0,0],[3,1,1,0,100],[4,1,1,0,0.3],[5,1,0,0,1e6],[6,1,1,4,12],[7,1,1,0.4,0.9],[8,1,1,18,24]]

                    else:
                        p0 = [70.0, 6.0, np.max(yf), np.max(yf)/50.0, 0.002, 5e4, 10.0, 0.5 , 17.0]
                        widthMinimum = 4.75
                        lims = [[0,1,1,50,100],[1,1,1,widthMinimum,6.75],[2,1,0,0,0],[3,1,1,0,100],[4,1,1,0,0.3],[5,1,0,0,1e6],[6,1,1,3,12],[7,1,1,0.3,0.6],[8,1,1,16,28]]

                if dataType == 'Ba':
                    widthMinimum = 0
                    if analysisType == 'lbl' or analysisType == 'vanilla':
                        p0 = [56, 8.0, 0.5*np.max(yQ),0,0,1.0*np.max(yQ),50.0,0.5,17.0,0]
                    elif analysisType == 'cmf':
                        p0 = [56, 8.0, 0.5*np.max(yQ),0,0,1.0*np.max(yQ),50.0,0.5,17.0,0]

                    lims = [[0,1,0,50,0],[1,1,0,4,0],[2,1,0,0,0],[3,1,0,0,0],[4,1,0,0,0],[5,1,0,0,0],[7,1,0,0,0],[8,1,0,10,0],[9,1,0,0,0]]

                # Fit data - If a bad fit is encountered, adjust parameters and refit
                while (x2 > 0.55*scaling or fitWidth == widthMinimum):

                    # Fit data
                    try:
                        _,pars,xfit,yfit = ef.arbFit(pFit3,xQ[c],yf[c],'Poisson',p0,lims)

                        # Calculate reduced chi2
                        x2 = np.sum((pFit3(xQ[c],pars[0]) - yf[c])**2/pFit3(xQ[c],pars[0]))/np.sum(c)
                        x2Arr.append(x2)
                        pArr.append(pars)

                        # Check if fit was good => Break
                        fitWidth = pars[0][1]
                        if x2 < 0.55*scaling and fitWidth != widthMinimum:
                            break

                        # If fit wasn't good, but there were already 20 fits made get the one with the lowest red. x2 and add to fit results
                        if len(x2Arr) > 20:
                            iMin = np.argmin(x2Arr)
                            pars = pArr[iMin]
                            x2 = x2Arr[iMin]
                            break

                        # Otherwise change initial fit parameter
                        p0[7] += 0.1*(0.5-np.random.rand())
                        p0[8] += (0.5-np.random.rand())
                    except (ValueError,TypeError):
                        # Otherwise change initial fit parameter
                        p0[7] += 0.1*(0.5-np.random.rand())
                        p0[8] += (0.5-np.random.rand())
                    if p0[7] < lims[7][3]: p0[7] = lims[7][3]
                    if p0[7] > lims[7][4]: p0[7] = lims[7][4]
                    if p0[8] < lims[8][3]: p0[8] = lims[8][3]
                    if p0[8] > lims[8][4]: p0[8] = lims[8][4]

                # Add fit results to the output arrays
                speQArr['PolyaBest'].append(pars[0][:])
                speQArr['PolyaErr'].append(pars[2][:])
                speQArr['Chi2'].append(x2)

            else:
                speQArr['PolyaBest'].append(pars[0][:])
                speQArr['PolyaErr'].append(pars[2][:])
                speQArr['Chi2'].append(-1)

            # Write data to HDF5 file
        for key in speQArr.keys():
            h5In.create_dataset('/SPEQ/%s/%s'%(analysisType,key),data=speQArr[key])

    h5In.close()
# ============================================================================
#                                Run program
# ============================================================================
if __name__ == '__main__':
#    args = ['', '/home/bjs66/csi/bjs-analysis/','Run-15-06-26-11-23-13','150711']
#    main(args)
    main(sys.argv)
















