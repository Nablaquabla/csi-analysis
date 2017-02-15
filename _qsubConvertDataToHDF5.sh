#!/bin/bash
#PBS -o /data2/coherent/data/csi/bjs-analysis/Logs/ConvertData.log
#PBS -e /data2/coherent/data/csi/bjs-analysis/Errs/ConvertData.err
#PBS -l walltime=00:45:00

/nfs_home/bjo/GitHub/csi-analysis/_convertDataToHDF5.py $mainDir $run $day
