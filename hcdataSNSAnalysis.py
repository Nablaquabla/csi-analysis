#!/usr/bin/env python
import os
import time as tm
import sys

# Main function handling all internals
# -----------------------------------------------------------------------------
def main(specificDay):       
    # Choose main directory, i.e. ~/csi/beam_on_data/Run-15-06-25-xyz/
    mainRunDir = '/data2/coherent/data/csi/'
    
    # Choose output directory, i.e. ~/output/Run-15-06-25-xyz/
    mainOutDir = '/data2/coherent/data/csi/bjs-analysis/'

    # Choose run to analyze
#    runDirs = ['Run-15-09-21-20-58-01'] 
#    runDirs = ['Run-17-02-08-00-00-00']
#    runDirs = ['Run-17-02-08-16-39-02']
#    runDirs = ['Run-15-06-25-12-53-44']
#    runDirs = ['Run-15-08-18-14-51-18']
#    runDirs = ['Run-15-08-31-00-23-36']
#    runDirs = ['Run-15-10-03-09-26-22']
#    runDirs = ['Run-15-10-29-15-56-36']
#    runDirs = ['Run-15-06-25-12-53-44','Run-15-06-26-11-23-13','Run-15-07-31-18-30-14']
#    runDirs = ['Run-15-08-18-14-51-18','Run-15-08-31-00-23-36'] 
    runDirs = ['Run-15-09-23-21-16-00','Run-15-10-03-09-26-22','Run-15-10-13-13-27-09']
#    runDirs = ['Run-15-10-21-13-12-27','Run-15-10-29-15-56-36','Run-15-11-09-11-30-13']
#    runDirs = ['Run-15-11-20-11-34-48','Run-15-11-24-15-35-32','Run-15-12-14-11-21-45']
#    runDirs = ['Run-15-12-26-08-30-40','Run-16-01-07-12-16-36','Run-16-02-02-16-26-26']
#    runDirs = ['Run-16-02-15-13-46-34','Run-16-02-29-11-54-20','Run-16-03-09-13-00-14']
#    runDirs = ['Run-16-03-22-18-09-33','Run-16-03-30-12-44-57','Run-16-04-12-11-54-27']
#    runDirs = ['Run-16-04-20-11-22-48','Run-16-05-05-14-08-52','Run-16-05-12-14-07-59']
#    runDirs = ['Run-16-05-17-14-40-34','Run-16-06-02-12-35-56','Run-16-06-17-12-09-12']
#    runDirs = ['Run-16-06-27-17-50-08','Run-16-07-06-18-25-19','Run-16-07-12-11-44-55']
#    runDirs = ['Run-16-07-18-11-50-24','Run-16-07-21-11-59-39','Run-16-07-28-12-49-17']
#    runDirs = ['Run-16-08-04-17-23-52','Run-16-08-09-00-29-54','Run-16-08-16-00-22-26']
#    runDirs = ['Run-16-08-27-11-33-40','Run-16-08-30-11-37-42','Run-16-09-06-15-23-15']
#    runDirs = ['Run-16-09-15-15-23-58','Run-16-09-26-15-34-10']
     
    subdirs = {}
    days_in = {}
    for run in runDirs:
        possibleSubDirs = ['beam_off_data','beam_on_data','sns_data']
        for psd in possibleSubDirs:
            possibleRuns = os.listdir(mainRunDir + psd)
	    # print possibleRuns
            if run in possibleRuns:
                subdirs[run] = psd
                days_in[run] = [x for x in os.listdir(mainRunDir + psd + '/' + run) if 'Settings' not in x]
            
    for run in runDirs:
        # Iterate through all days in a given run folder, create a condor file and run it.
        if specificDay != 'None':
            if specificDay in days_in[run]: 
                days_in[run] = [specificDay]
            else:
                days_in[run] = []          
        for day in days_in[run]:
            # Prepare paths for further processing
            dataRunDir = mainRunDir + '%s/%s/%s'%(subdirs[run],run,day)
            outDir = mainOutDir + '%s/%s'%(run,day)
        
            # Create output directory if it does not exist
            if not os.path.exists(outDir):
                os.makedirs(outDir)   

            # Wait for the dir to be created such that no race condition occurs.
            tm.sleep(1.0)
            
            # Get all times within the day folder chosen and prepare condor submit files
            tList = [x.split('.')[0] for x in os.listdir(dataRunDir)]
            cmd = 'qsub -t 1-%i -V /nfs_home/bjo/GitHub/csi-analysis/_qsubSNSAnalysis.sh -v analysisMode="1",dataDir="%s",outDir="%s",specificTime="0",time="0"'%(len(tList), dataRunDir, outDir)
#            print cmd
            os.system(cmd)
if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main('None')
