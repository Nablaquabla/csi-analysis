#!/bin/bash
#PBS -o /dev/null
#PBS -e /dev/null
#PBS -l nodes=1:ppn=1
#PBS -l walltime=00:01:00
#PBS -l mem=400mb
if [ $specificTime == "1" ]; then
  fileNumber=$time
else
  let fileNumber=PBS_ARRAYID-1
fi
/nfs_home/bjo/GitHub/csi-analysis/hcdataCsIAnalysis $analysisMode $dataDir $fileNumber $outDir $specificTime
