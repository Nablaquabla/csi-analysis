#!/bin/bash
#PBS -o /dev/null
#PBS -e /dev/null
#PBS -l nodes=1:ppn=1
#PBS -l walltime=00:45:00
#PBS -l mem=750mb
/nfs_home/bjo/GitHub/csi-analysis/_convertDataToHDF5.py $mainDir $run $day
