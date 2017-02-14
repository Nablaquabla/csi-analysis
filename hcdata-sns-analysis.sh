#!/usr/bin/bash
progPath=/nfs_home/bjo/GitHub/csi-analysis/csi-analysis
dataDir=/data2/coherent/data/csi/beam_on_data/Run-15-06-25-12-53-44/150625/
outDir=/data2/coherent/data/csi/bjs-analysis/Run-15-06-25-12-53-44/150625/
mkdir -p $outDir
sleep 0.5
qsub $progPath -v 1,$dataDir,0,$outDir
