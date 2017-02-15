#!/bin/bash
currentAnalysisMode=1
currentDataDir=PYTHON_INSERT_DATADIR
currentOutDir=PYTHON_INSERT_OUTDIR
currentProcessNumber=0
mkdir -p $currentOutDir
sleep 1.0
for entry in "$currentDataDir"/*
do
  if [ -f "$entry" ]; then
    if [ $currentProcessNumber -lt 100 ]; then
      echo $currentProcessNumber
      qsub -V /nfs_home/bjo/GitHub/csi-analysis/hcdata-sns-analysis.sh -v analysisMode="1",dataDir="$currentDataDir",processNumber="$currentProcessNumber",outDir="$currentOutDir"
    fi
    let currentProcessNumber+=1
  fi
done
# qsub -V /nfs_home/bjo/GitHub/csi-analysis/hcdata-sns-analysis.sh -v analysisMode="1",dataDir="$currentDataDir",processNumber="$currentProcessNumber",outDir="$currentOutDir"
