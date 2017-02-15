#!/bin/bash
#PBS -o /data2/coherent/data/csi/bjs-analysis/Run.log
#PBS -e /data2/coherent/data/csi/bjs-analysis/Run.err
#PBS -l walltime=00:01:00
/nfs_home/bjo/GitHub/csi-analysis/csi-analysis 1 $dataDir $processNumber $outDir 0
