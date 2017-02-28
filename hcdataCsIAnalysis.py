#!/user/bin/env python
import sys
import subprocess

def main(args):
    analysisMode = args[1]
    dataDir = args[2]
    fileNumber = args[3]
    outDir = args[4]
    specificTime = args[5]
    time = args[6]
    
    if specificTime == '0':
        for fileIndex in range(int(fileNumber)):
            cmd = ['/nfs_home/bjo/GitHub/csi-analysisi/hcdataCsIAnalysis',analysisMode,dataDir,fileIndex,outDir,specificTime]
            subprocess.call(cmd)
            if fileIndex > 10:
                break

    else:
        cmd = ['/nfs_home/bjo/GitHub/csi-analysisi/hcdataCsIAnalysis',analysisMode,dataDir,time,outDir,specificTime]
        subprocess.call(cmd)
    
    return

if __name__ == "__main__":
    main(sys.argv)
