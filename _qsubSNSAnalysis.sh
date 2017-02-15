#!/bin/bash
#PBS -o /data2/coherent/data/csi/bjs-analysis/Logs/Run.log
#PBS -e /data2/coherent/data/csi/bjs-analysis/Errs/Run.err
#PBS -l nodes=1:ppn=1
#PBS -l walltime=00:01:00
#PBS -l mem=400mb
if [ $specificTime == "1" ]; then
  fileNumber=$time
else
  let fileNumber=PBS_ARRAYID-1
fi
echo $fileNumber
echo $analysisMode
echo $dataDir
#/nfs_home/bjo/GitHub/csi-analysis/csi-analysis $analysisMode $dataDir $fileNumber $outDir $specificTime
