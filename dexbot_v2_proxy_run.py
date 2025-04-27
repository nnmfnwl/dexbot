#!/usr/bin/env python3

# ~ MIT License

# ~ Copyright (c) 2020 - 2025 NNMFNWL

# ~ Permission is hereby granted, free of charge, to any person obtaining a copy
# ~ of this software and associated documentation files (the "Software"), to deal
# ~ in the Software without restriction, including without limitation the rights
# ~ to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# ~ copies of the Software, and to permit persons to whom the Software is
# ~ furnished to do so, subject to the following conditions:

# ~ The above copyright notice and this permission notice shall be included in all
# ~ copies or substantial portions of the Software.

# ~ THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# ~ IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# ~ FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# ~ AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# ~ LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# ~ OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# ~ SOFTWARE.

import time
import subprocess
import argparse
import sys

# main function
if __name__ == '__main__':
    
    # parse configuration argument
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--restore', help='try to restore cached data', action='store_true')
    
    args = parser.parse_args()
    restore = args.restore
    
    restore_arg = ""
    if restore:
        restore_arg = "--restore True"
        
    # run dexbot proxy process:
    # case1: if exception rises, try to restart dexbot proxy process again
    # case2: if exit success, exit program
    while 1:
        # run dexbot proxy 
        print("[I] starting dexbot proxy")
        result = subprocess.run("python3 dexbot_v2_proxy.py " + restore_arg, shell=True)
        # if dexbot proxy process exit success exit program
        if result.returncode == 0:
            break
        
        # if dexbot proxy process exit with error try to restart with restore true again
        restore_arg = "--restore True"
        # print crash warning
        print("[W] dexbot proxy crashed, restarting")
        # wait a while, we do not want to burn cpu by recovery process...
        time.sleep(3)
        # loop while to start again
        
sys.exit(0)

