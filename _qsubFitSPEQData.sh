#!/bin/bash
#PBS -o /data2/coherent/data/csi/bjs-analysis/Logs/FitData.log
#PBS -e /data2/coherent/data/csi/bjs-analysis/Errs/ConvertData.err
#PBS -l nodes=1:ppn=1
#PBS -l walltime=04:00:00
#PBS -l mem=750mb
/nfs_home/bjo/GitHub/csi-analysis/_fitSPEQData.py $mainDir $run $day
