#!/bin/bash
#PBS -o /data2/coherent/data/csi/bjs-analysis/output/
#PBS -e /data2/coherent/data/csi/bjs-analysis/error/
#PBS -l nodes=1:ppn=1
#PBS -l walltime=02:00:00
#PBS -l mem=400mb
/nfs_home/bjo/GitHub/csi-analysis/_getSPEQIndex.py $mainDir $run
