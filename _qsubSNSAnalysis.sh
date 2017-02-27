#!/bin/bash
#PBS -o /dev/null
#PBS -e /dev/null
#PBS -l nodes=1:ppn=1
#PBS -l walltime=00:10:00
#PBS -l mem=400mb
/nfs_home/bjo/GitHib/csi-analysis/_hcdataCsIAnalysis.py $analysisMode $dataDir $fileNumber $outDir $specificTime $time
