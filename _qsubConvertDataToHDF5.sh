#!/bin/bash
#PBS -o /data2/coherent/data/csi/bjs-analysis/output/
#PBS -e /data2/coherent/data/csi/bjs-analysis/error/
#PBS -l nodes=1:ppn=1
#PBS -l walltime=12:45:00
#PBS -l mem=750mb
/nfs_home/bjo/GitHub/csi-analysis/_convertDataToHDF5.py $mainDir $run $day
