#!/bin/bash
#PBS -o /data2/coherent/data/csi/bjs-analysis/Logs/Run.log
#PBS -e /data2/coherent/data/csi/bjs-analysis/Errs/Run.err
#PBS -l walltime=00:01:00
let fileNumber=PBS_ARRAYID-1
/nfs_home/bjo/GitHub/csi-analysis/csi-analysis 1 $dataDir $fileNumber $outDir 0
