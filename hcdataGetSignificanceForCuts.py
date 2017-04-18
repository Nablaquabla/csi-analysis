#!/usr/bin/env python
import os
import time as tm

# Main function handling all internals
# -----------------------------------------------------------------------------
def main():
    for minPEinIW in [6,7,8]:
        cmd = 'qsub -V /nfs_home/bjo/GitHub/csi-analysis/_qsubGetSignificanceForCuts.sh -v minPEinIW="%s"'%(minPEinIW)
        os.system(cmd)
        tm.sleep(1)

if __name__ == '__main__':
    main()



























