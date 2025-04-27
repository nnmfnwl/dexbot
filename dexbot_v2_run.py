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
    parser.add_argument('--exitonerror', type=int, help='Maximum number of errors to be occurred before process exit even with error(default=0, do not exit on error)', default=0)
    parser.add_argument('--config', type=str, help='python configuration file', default=None)
    parser.add_argument('--cancelall', help='cancel all orders and exit', action='store_true')
    parser.add_argument('--cancelmarket', help='cancel all orders in market pair specified by --config file', action='store_true')
    parser.add_argument('--canceladdress', help='cancel all orders in market pair and address specified by --config file', action='store_true')
    args = parser.parse_args()
    exitonerror = int(args.exitonerror)
    config = args.config
    cancelall = args.cancelall
    cancelmarket = args.cancelmarket
    canceladdress = args.canceladdress
    restore = ""
    
    # check exit on error validity
    if exitonerror < 0:
        print("[E] --exitonerror number is invalid <{}>".format(config))
        sys.exit(1)
    errors1=0
    errors2=0
    
    # check if configuration argument is set
    if config is None:
        print("[E] --config file is none <{}>".format(config))
        sys.exit(1)
    
    print("[I] --config file <{}>".format(config))
    
    # try to import configuration file
    cfg = __import__(config)
    
    # check configuration file
    if not cfg.botconfig:
        print("[E] --config file is invalid")
        sys.exit(1)
    
    # update configuration to be valid
    cfg.botconfig = cfg.botconfig.replace(" --", "--")
    cfg.botconfig = cfg.botconfig.replace("--", " --")
    
    print("[I] --config arguments <{}>".format(cfg.botconfig))
    
    # check if cancel all or market orders orders
    cancel_orders_arg = ""
    if cancelall:
        cancel_orders_arg = "--cancelall"
    if cancelmarket:
        if cancel_orders_arg != "":
            print("[E] cancelall|cancelmarket|canceladdress only one argument is allowed".format())
            sys.exit(1)
        cancel_orders_arg = "--cancelmarket"
    if canceladdress:
        if cancel_orders_arg != "":
            print("[E] cancelall|cancelmarket|canceladdress only one argument is allowed".format())
            sys.exit(1)
        cancel_orders_arg = "--canceladdress"
        
    # run dexbot process:
    # case1: if exception rises, try to recover from situation, cancel all open orders and restart dexbot process again
    # case2: if exit success, exit program
    while 1:
        # run dexbot
        print("[I] starting dexbot")
        result = subprocess.run("python3 dexbot_v2.py --config " + config + " " + restore + " " + cfg.botconfig + " " + cancel_orders_arg, shell=True)
        # if dexbot process exit success exit program
        if result.returncode == 0:
            break
        
        restore = "--restore True"
        
        # if dexbot process exit with error try to cancel all existing orders and try to start bot again
        while 1:
            # cancel all orders
            print("[W] dexbot crashed, clearing open orders")
            # wait a while, we do not want to burn cpu by recovery process...
            time.sleep(3)
            # try to cancel orders
            result2 = subprocess.run("python3 dexbot_v2.py --config " + config + " " + restore + " " + cfg.botconfig + " --canceladdress", shell=True)
            # check if cancel all orders success or try to do it again
            if result2.returncode == 0:
                break
            # wait a while on error to try again
            print("[W] dexbot crash >> recovery try >> cancel orders >> internal error >> failed")
            
            # check exit on error for cancel orders
            errors2 +=1
            if exitonerror > 0 and errors2 >= exitonerror:
                print("[W] dexbot crash >> recovery try >> maximum errors2 reached >> exit")
                break
        
        # check exit on error for main loop
        errors1 +=1
        if exitonerror > 0 and errors1 >= exitonerror:
            print("[W] dexbot crash >> recovery try >> maximum errors1 reached >> exit")
            break
        
sys.exit(0)
