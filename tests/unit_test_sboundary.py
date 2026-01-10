#!/usr/bin/env python3

import time
import random
import argparse
import sys
import logging

import features.glob as glob
from features.tmp_cfg import *
from features.sboundary import *

from collections import deque

# nicely ugly but effective pricing hack ))
glob.test_sboundary_price = deque()
def unit_test__sboundary__get_price_1(maker, taker):
    ret = glob.test_sboundary_price.popleft()
    print('\n>> INFO >> TEST >> unit_test__sboundary__get_price_1 >> <{}/{} is <{}>>\n'.format(maker, taker, ret))
    return ret

def unit_test__sboundary():
    
    print('>> INFO >> TEST 21 >> sboundary__init_preconfig')
    feature__tmp_cfg__init_preconfig__()
    sboundary__init_preconfig__()
    
    parser = argparse.ArgumentParser()
    
    print('>> INFO >> TEST 27 >> sboundary__load_config_define')
    feature__tmp_cfg__load_config_define(parser, argparse)
    sboundary__load_config_define(parser, argparse)
    
    args = parser.parse_args()
    
    # force arguments
    args.config = "unit_test_sboundaryy"
    args.sboundary_asset = "USDT"
    
    args.sboundary_max = float(4)
    args.sboundary_min = float(1)
    
    args.sboundary_max_track_asset = False
    args.sboundary_min_track_asset = False
    
    args.sboundary_price_reverse = False
    
    args.sboundary_max_cancel = True
    args.sboundary_max_exit = True
    args.sboundary_min_cancel = True
    args.sboundary_min_exit = False
    
    print('>> INFO >> TEST 50 >> sboundary__load_config_postparse')
    feature__tmp_cfg__load_config_postparse(args)
    sboundary__load_config_postparse(args)
    
    ####################################################################
    ## Test configuration verification 
    error_num = 0
    crazy_num = 0
    
    error_num_tmp, crazy_num_tmp = feature__tmp_cfg__load_config_verify()
    error_num += error_num_tmp
    crazy_num += crazy_num_tmp
    
    print('>> INFO >> TEST 63 >> sboundary__load_config_verify')
    error_num_tmp, crazy_num_tmp = sboundary__load_config_verify()
    error_num += error_num_tmp
    crazy_num += crazy_num_tmp
    if error_num == 0 and crazy_num == 0:
        print('>> INFO >> TEST 68 >> sboundary__load_config_verify >> success {}'.format(error_num))
    else:
        print('>> ERROR >> TEST 70 >> sboundary__load_config_verify >> failed {}'.format(error_num))
        sys.exit(1)
    
    ####################################################################
    ## Test pricing init
    
    print('>> INFO >> TEST 76 >> sboundary__pricing_init, pricing is set to 0.01, so return should be same')
    glob.test_sboundary_price.append(0.01)
    price_boundary = sboundary__pricing_init("BLOCK", "BTC", 'none', unit_test__sboundary__get_price_1)
    if price_boundary == 0.01:
        print('>> INFO >> TEST 80 >> sboundary__pricing_init >> success')
    else:
        print('** ERROR >> TEST 82 >> sboundary__pricing_init >> failed')
        sys.exit(1)
    
    ####################################################################
    ## test pricing update with asset track disabled
    
    print('>> INFO >> TEST 88 >> sboundary__pricing_update, pricing is set to 0.03, but but no tracking so, it even should not check the price')
    glob.test_sboundary_price.append(0.03)
    price_boundary = sboundary__pricing_update()
    if price_boundary == 0.01:
        print('>> INFO >> TEST 92 >> sboundary__pricing_init >> success')
    else:
        print('** ERROR >> TEST 94 >> sboundary__pricing_init >> failed')
        sys.exit(1)
    glob.test_sboundary_price.popleft()
    
    ####################################################################
    ## test max boundary hit no
    
    print('>> INFO >> TEST 100 >> sboundary__check_max 0.04')
    ret_hit_exp = False
    ret_exit_exp = False
    ret_cancel_exp = False
    
    ret_hit, ret_exit, ret_cancel, ret_price = sboundary__check_max(0.04)
    if ret_hit == ret_hit_exp and ret_exit == ret_exit_exp and ret_cancel == ret_cancel_exp:
        print('>> INFO >> TEST 107 >> sboundary__check_max >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
    else:
        print('** ERROR >> TEST 109 >> sboundary__check_max >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
        sys.exit(1)
    
    ####################################################################
    ## test max boundary hit yes
    
    print('>> INFO >> TEST 115 >> sboundary__check_max 0.041')
    ret_hit_exp = True
    ret_exit_exp = True
    ret_cancel_exp = True
    
    ret_hit, ret_exit, ret_cancel, ret_price = sboundary__check_max(0.041)
    if ret_hit == ret_hit_exp and ret_exit == ret_exit_exp and ret_cancel == ret_cancel_exp:
        print('>> INFO >> TEST 122 >> sboundary__check_max >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
    else:
        print('** ERROR >> TEST 124 >> sboundary__check_max >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
        sys.exit(1)
    
    ####################################################################
    ## test min boundary hit no
    
    print('>> INFO >> TEST 130 >> sboundary__check_min 0.01')
    ret_hit_exp = False
    ret_exit_exp = False
    ret_cancel_exp = False
    
    ret_hit, ret_exit, ret_cancel, ret_price = sboundary__check_min(0.01)
    if ret_hit == ret_hit_exp and ret_exit == ret_exit_exp and ret_cancel == ret_cancel_exp:
        print('>> INFO >> TEST 137 >> sboundary__check_min >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
    else:
        print('** ERROR >> TEST 139 >> sboundary__check_min >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
        sys.exit(1)
        
    ####################################################################
    ## test min boundary hit yes
    
    print('>> INFO >> TEST 145 >> sboundary__check_min 0.0099')
    ret_hit_exp = True
    ret_exit_exp = False
    ret_cancel_exp = True
    
    ret_hit, ret_exit, ret_cancel, ret_price = sboundary__check_min(0.0099)
    if ret_hit == ret_hit_exp and ret_exit == ret_exit_exp and ret_cancel == ret_cancel_exp:
        print('>> INFO >> TEST 152 >> sboundary__check_min >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
    else:
        print('** ERROR >> TEST 154 >> sboundary__check_min >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
        sys.exit(1)
        
    ####################################################################
    ## test price recompute
    
    print('>> INFO >> TEST 160 >> sboundary__recompute_price(1)')
    ret_hit, ret_exit, ret_cancel, price = sboundary__check(1)
    if price == 0.04:
        print('>> INFO >> TEST 163 >> sboundary__recompute_price(1) >> {} OK'.format(price))
    else:
        print('>> ERROR >> TEST 165 >> sboundary__recompute_price(1) >> {}'.format(price))
        sys.exit(1)
        
    print('>> INFO >> TEST 168 >> sboundary__recompute_price(0.001)')
    ret_hit, ret_exit, ret_cancel, price = sboundary__check(0.001)
    if price == 0.01:
        print('>> INFO >> TEST 171 >> sboundary__recompute_price(1) >> {} OK'.format(price))
    else:
        print('>> ERROR >> TEST 173 >> sboundary__recompute_price(1) >> {}'.format(price))
        sys.exit(1)
        
    ####################################################################
    ####################################################################
    ## test 2 reset static boundary with another values
    sboundary__init_preconfig__()
    
    d.sboundary__price_initial = 0
    d.sboundary__price_current = 0
    
    # original static boundary setup BLOCK USDT BTC
    # pricing                        1     0.01 0.001
    # reversed static boundary setup BTC USDT BLOCK
    # pricing                        1   10   1000
    args.sboundary_asset = "USDT"
    
    args.sboundary_max = float(0.02)
    args.sboundary_min = float(0.009)
    
    args.sboundary_max_track_asset = False
    args.sboundary_min_track_asset = False
    
    args.sboundary_price_reverse = True
    
    args.sboundary_max_cancel = True
    args.sboundary_max_exit = True
    args.sboundary_min_cancel = True
    args.sboundary_min_exit = False
    
    print('>> INFO >> TEST 199 >> sboundary__load_config_postparse')
    sboundary__load_config_postparse(args)
    
    ####################################################################
    ## Test 2 configuration verification 
    error_num = 0
    crazy_num = 0
    
    print('>> INFO >> TEST 207 >> sboundary__load_config_verify')
    error_num_tmp, crazy_num_tmp = sboundary__load_config_verify()
    error_num += error_num_tmp
    crazy_num += crazy_num_tmp
    if error_num == 0 and crazy_num == 0:
        print('>> INFO >> TEST 212 >> sboundary__load_config_verify >> success {}'.format(error_num))
    else:
        print('>> ERROR >> TEST 214 >> sboundary__load_config_verify >> failed {}'.format(error_num))
        sys.exit(1)
    
    ####################################################################
    ## Test 2 pricing init reverse
    
    print('>> INFO >> TEST 220 >> sboundary__pricing_init')
    glob.test_sboundary_price.append(1000) # BTC to 
    glob.test_sboundary_price.append(100)
    price_boundary = sboundary__pricing_init("BTC", "BLOCK", 'none', unit_test__sboundary__get_price_1)
    if price_boundary == 100:
        print('>> INFO >> TEST 224 >> sboundary__pricing_init >> {} >> success'.format(price_boundary))
    else:
        print('** ERROR >> TEST 225 >> sboundary__pricing_init >> {} >> failed'.format(price_boundary))
        sys.exit(1)
    
    if c.sboundary__min == 9 and c.sboundary__max == 20:
        print('>> INFO >> TEST 237 >> MIN/MAX {}/{} >> success'.format(c.sboundary__min, c.sboundary__max))
    else:
        print('>> INFO >> TEST 237 >> MIN/MAX {}/{} >> failed'.format(c.sboundary__min, c.sboundary__max))
    
    ####################################################################
    ## test 2 pricing update with asset track disabled
    
    print('>> INFO >> TEST 232 >> sboundary__pricing_update')
    glob.test_sboundary_price=0.03
    price_boundary = sboundary__pricing_update()
    if price_boundary == 100:
        print('>> INFO >> TEST 236 >> sboundary__pricing_init >> {} >> success'.format(price_boundary))
    else:
        print('** ERROR >> TEST 238 >> sboundary__pricing_init >> {} >> failed'.format(price_boundary))
        sys.exit(1)
    
    ####################################################################
    ## test 2 max boundary hit no
    
    print('>> INFO >> TEST 244 >> sboundary__check_max 100')
    ret_hit_exp = False
    ret_exit_exp = False
    ret_cancel_exp = False
    
    ret_hit, ret_exit, ret_cancel, ret_price = sboundary__check_max(1999)
    if ret_hit == ret_hit_exp and ret_exit == ret_exit_exp and ret_cancel == ret_cancel_exp:
        print('>> INFO >> TEST 251 >> sboundary__check_max >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
    else:
        print('** ERROR >> TEST 253 >> sboundary__check_max >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
        sys.exit(1)
    
    ####################################################################
    ## test 2 max boundary hit yes
    
    print('>> INFO >> TEST 259 >> sboundary__check_max 101')
    ret_hit_exp = True
    ret_exit_exp = True
    ret_cancel_exp = True
    
    ret_hit, ret_exit, ret_cancel, ret_price = sboundary__check_max(2001)
    if ret_hit == ret_hit_exp and ret_exit == ret_exit_exp and ret_cancel == ret_cancel_exp:
        print('>> INFO >> TEST 266 >> sboundary__check_max >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
    else:
        print('** ERROR >> TEST 268 >> sboundary__check_max >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
        sys.exit(1)
    
    ####################################################################
    ## test 2 min boundary hit no
    
    print('>> INFO >> TEST 274 >> sboundary__check_min 25')
    ret_hit_exp = False
    ret_exit_exp = False
    ret_cancel_exp = False
    
    ret_hit, ret_exit, ret_cancel, ret_price = sboundary__check_min(900)
    if ret_hit == ret_hit_exp and ret_exit == ret_exit_exp and ret_cancel == ret_cancel_exp:
        print('>> INFO >> TEST 281 >> sboundary__check_min >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
    else:
        print('** ERROR >> TEST 281 >> sboundary__check_min >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
        sys.exit(1)
        
    ####################################################################
    ## test 2 min boundary hit yes
    
    print('>> INFO >> TEST 289 >> sboundary__check_min 24')
    ret_hit_exp = True
    ret_exit_exp = False
    ret_cancel_exp = True
    
    ret_hit, ret_exit, ret_cancel, ret_price = sboundary__check_min(899)
    if ret_hit == ret_hit_exp and ret_exit == ret_exit_exp and ret_cancel == ret_cancel_exp:
        print('>> INFO >> TEST 296 >> sboundary__check_min >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
    else:
        print('** ERROR >> TEST 296 >> sboundary__check_min >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
        sys.exit(1)
        
    ####################################################################
    ## test 2 price recompute
    
    print('>> INFO >> TEST 318 >> sboundary__recompute_price(1)')
    ret_hit, ret_exit, ret_cancel, ret_price = sboundary__check(2001)
    if ret_price == 2000:
        print('>> INFO >> TEST 321 >> sboundary__recompute_price(1) >> {} OK'.format(ret_price))
    else:
        print('>> ERROR >> TEST 323 >> sboundary__recompute_price(1) >> {}'.format(ret_price))
        sys.exit(1)
        
    print('>> INFO >> TEST 326 >> sboundary__recompute_price(0.001)')
    ret_hit, ret_exit, ret_cancel, ret_price = sboundary__check(899)
    if ret_price == 900:
        print('>> INFO >> TEST 329 >> sboundary__recompute_price(1) >> {} OK'.format(ret_price))
    else:
        print('>> ERROR >> TEST 331 >> sboundary__recompute_price(1) >> {}'.format(ret_price))
        sys.exit(1)
