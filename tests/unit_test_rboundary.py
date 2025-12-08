#!/usr/bin/env python3

import time
import random
import argparse
import sys
import logging

import features.glob as glob
from features.tmp_cfg import *
from features.rboundary import *

glob.test_rboundary_price = 0

def unit_test__rboundary__get_price_1(maker, taker):
    print('\n>> INFO >> TEST >> unit_test__rboundary__get_price_1 >> <{}/{} is <{}>>\n'.format(maker, taker, glob.test_rboundary_price))
    return glob.test_rboundary_price

def unit_test__rboundary():
    
    print('>> INFO >> TEST >> rboundary__init_preconfig')
    feature__tmp_cfg__init_preconfig__()
    rboundary__init_preconfig__()
    
    parser = argparse.ArgumentParser()
    
    print('>> INFO >> TEST >> rboundary__load_config_define')
    feature__tmp_cfg__load_config_define(parser, argparse)
    rboundary__load_config_define(parser, argparse)
    
    args = parser.parse_args()
    
    # force arguments
    args.config = "unit_test_rboundaryy"
    args.rboundary_asset = "USDT"
    
    d.rboundary__price_initial = 0
    d.rboundary__price_current = 0
    
    args.rboundary_max = float(4)
    args.rboundary_min = float(1)
    
    args.rboundary_max_track_asset = False
    args.rboundary_min_track_asset = False
    
    args.rboundary__price_reverse = False
    
    args.rboundary_max_cancel = True
    args.rboundary_max_exit = True
    args.rboundary_min_cancel = True
    args.rboundary_min_exit = False
    
    print('>> INFO >> TEST >> rboundary__load_config_postparse')
    feature__tmp_cfg__load_config_postparse(args)
    rboundary__load_config_postparse(args)
    
    ####################################################################
    ## Test configuration verification 
    error_num = 0
    crazy_num = 0
    
    error_num_tmp, crazy_num_tmp = feature__tmp_cfg__load_config_verify()
    error_num += error_num_tmp
    crazy_num += crazy_num_tmp
    
    print('>> INFO >> TEST >> rboundary__load_config_verify')
    error_num_tmp, crazy_num_tmp = rboundary__load_config_verify()
    error_num += error_num_tmp
    crazy_num += crazy_num_tmp
    if error_num == 0 and crazy_num == 0:
        print('>> INFO >> TEST >> rboundary__load_config_verify >> success {}'.format(error_num))
    else:
        print('>> ERROR >> TEST >> rboundary__load_config_verify >> failed {}'.format(error_num))
        sys.exit(1)
    
    ####################################################################
    ## Test pricing init
    
    print('\n>> INFO >> TEST >> rboundary__pricing_init')
    glob.test_rboundary_price=0.01
    price_boundary = rboundary__pricing_init("BLOCK", "BTC", 'none', unit_test__rboundary__get_price_1)
    if price_boundary == 0.0001:
        print('>> INFO >> TEST >> rboundary__pricing_init >> success')
    else:
        print('** ERROR >> TEST >> rboundary__pricing_init >> return {} >> failed'.format(price_boundary))
        sys.exit(1)
    
    ####################################################################
    ## test pricing update with asset track disabled
    
    print('>> INFO >> TEST >> rboundary__pricing_update')
    glob.test_rboundary_price=0.03
    price_boundary = rboundary__pricing_update()
    if price_boundary == 0.0001:
        print('>> INFO >> TEST >> rboundary__pricing_update >> {} >> success'.format(price_boundary))
    else:
        print('** ERROR >> TEST >> rboundary__pricing_update >> return {} >> failed'.format(price_boundary))
        sys.exit(1)
    
    ####################################################################
    ## test max boundary hit no
    
    print('>> INFO >> TEST >> rboundary__check_max 0.04')
    ret_hit_exp = False
    ret_exit_exp = False
    ret_cancel_exp = False
    
    ret_hit, ret_exit, ret_cancel, ret_price = rboundary__check_max(0.0004)
    if ret_hit == ret_hit_exp and ret_exit == ret_exit_exp and ret_cancel == ret_cancel_exp:
        print('>> INFO >> TEST >> rboundary__check_max >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
    else:
        print('** ERROR >> TEST >> rboundary__check_max >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
        sys.exit(1)
    
    ####################################################################
    ## test max boundary hit yes
    
    print('>> INFO >> TEST >> rboundary__check_max 0.00041')
    ret_hit_exp = True
    ret_exit_exp = True
    ret_cancel_exp = True
    
    ret_hit, ret_exit, ret_cancel, ret_price = rboundary__check_max(0.00041)
    if ret_hit == ret_hit_exp and ret_exit == ret_exit_exp and ret_cancel == ret_cancel_exp:
        print('>> INFO >> TEST >> rboundary__check_max >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
    else:
        print('** ERROR >> TEST >> rboundary__check_max >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
        sys.exit(1)
    
    ####################################################################
    ## test min boundary hit no
    
    print('>> INFO >> TEST >> rboundary__check_min 0.0001')
    ret_hit_exp = False
    ret_exit_exp = False
    ret_cancel_exp = False
    
    ret_hit, ret_exit, ret_cancel, ret_price = rboundary__check_min(0.0001)
    if ret_hit == ret_hit_exp and ret_exit == ret_exit_exp and ret_cancel == ret_cancel_exp:
        print('>> INFO >> TEST >> rboundary__check_min >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
    else:
        print('** ERROR >> TEST >> rboundary__check_min >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
        sys.exit(1)
        
    ####################################################################
    ## test min boundary hit yes
    
    print('>> INFO >> TEST >> rboundary__check_min 0.000099')
    ret_hit_exp = True
    ret_exit_exp = False
    ret_cancel_exp = True
    
    ret_hit, ret_exit, ret_cancel, ret_price = rboundary__check_min(0.000099)
    if ret_hit == ret_hit_exp and ret_exit == ret_exit_exp and ret_cancel == ret_cancel_exp:
        print('>> INFO >> TEST >> rboundary__check_min >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
    else:
        print('** ERROR >> TEST >> rboundary__check_min >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
        sys.exit(1)
        
    ####################################################################
    ## test price recompute
    
    print('>> INFO >> TEST >> rboundary__check(1)')
    ret_hit, ret_exit, ret_cancel, ret_price = rboundary__check(1)
    if ret_price == 0.0004:
        print('>> INFO >> TEST >> rboundary__check(1) >> {} OK'.format(ret_price))
    else:
        print('>> ERROR >> TEST >> rboundary__check(1) >> {}'.format(ret_price))
        sys.exit(1)
        
    print('>> INFO >> TEST >> rboundary__check(0.001)')
    ret_hit, ret_exit, ret_cancel, ret_price = rboundary__check(0.0001)
    if ret_price == 0.0001:
        print('>> INFO >> TEST >> rboundary__check(1) >> {} OK'.format(ret_price))
    else:
        print('>> ERROR >> TEST >> rboundary__check(1) >> {}'.format(ret_price))
        sys.exit(1)
        
    ####################################################################
    ####################################################################
    ## test 2 reset relative boundary with another values
    
    d.rboundary__price_initial = 0
    d.rboundary__price_current = 0
    
    # force arguments
    args.rboundary_asset = "USDT"
    
    args.rboundary_max = float(3)
    args.rboundary_min = float(0.9)
    
    args.rboundary_max_track_asset = False
    args.rboundary_min_track_asset = False
    
    args.rboundary_price_reverse = True
    
    args.rboundary_max_cancel = True
    args.rboundary_max_exit = True
    args.rboundary_min_cancel = True
    args.rboundary_min_exit = False
    
    print('>> INFO >> TEST 2 >> rboundary__load_config_postparse')
    rboundary__load_config_postparse(args)
    
    ####################################################################
    ## Test 2 configuration verification 
    error_num = 0
    crazy_num = 0
    
    print('>> INFO >> TEST 2 >> rboundary__load_config_verify')
    error_num_tmp, crazy_num_tmp = rboundary__load_config_verify()
    error_num += error_num_tmp
    crazy_num += crazy_num_tmp
    if error_num == 0 and crazy_num == 0:
        print('>> INFO >> TEST 2 >> rboundary__load_config_verify >> success {}'.format(error_num))
    else:
        print('>> ERROR >> TEST 2 >> rboundary__load_config_verify >> failed {}'.format(error_num))
        sys.exit(1)
    
    ####################################################################
    ## Test 2 pricing init reverse
    
    print('>> INFO >> TEST 2 >> rboundary__pricing_init 0.01')
    glob.test_rboundary_price=0.01
    price_boundary = rboundary__pricing_init("BTC", "BLOCK", 'none', unit_test__rboundary__get_price_1)
    if price_boundary == 10000:
        print('>> INFO >> TEST 227 >> rboundary__pricing_init >> {} >> success'.format(price_boundary))
    else:
        print('** ERROR >> TEST 229 >> rboundary__pricing_init >> {} >> failed'.format(price_boundary))
        sys.exit(1)
    
    ####################################################################
    ## test 2 pricing update with asset track disabled
    
    print('>> INFO >> TEST 2 >> rboundary__pricing_update 0.03')
    glob.test_rboundary_price=0.03
    price_boundary = rboundary__pricing_update()
    if price_boundary == 10000:
        print('>> INFO >> TEST 239 >> rboundary__pricing_update >> {} >> success'.format(price_boundary))
    else:
        print('** ERROR >> TEST 240 >> rboundary__pricing_update >> {} >> failed'.format(price_boundary))
        sys.exit(1)
    
    ####################################################################
    ## test 2 max boundary hit no
    
    print('>> INFO >> TEST 247 >> rboundary__check_max 400')
    ret_hit_exp = False
    ret_exit_exp = False
    ret_cancel_exp = False
    
    ret_hit, ret_exit, ret_cancel, ret_price = rboundary__check_max(30000)
    if ret_hit == ret_hit_exp and ret_exit == ret_exit_exp and ret_cancel == ret_cancel_exp:
        print('>> INFO >> TEST 254 >> rboundary__check_max >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
    else:
        print('** ERROR >> TEST 256 >> rboundary__check_max >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
        sys.exit(1)
    
    ####################################################################
    ## test 2 max boundary hit yes
    
    print('>> INFO >> TEST 2 >> rboundary__check_max 101')
    ret_hit_exp = True
    ret_exit_exp = True
    ret_cancel_exp = True
    
    ret_hit, ret_exit, ret_cancel, ret_price = rboundary__check_max(30000.1)
    if ret_hit == ret_hit_exp and ret_exit == ret_exit_exp and ret_cancel == ret_cancel_exp:
        print('>> INFO >> TEST 2 >> rboundary__check_max >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
    else:
        print('** ERROR >> TEST 2 >> rboundary__check_max >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
        sys.exit(1)
    
    ####################################################################
    ## test 2 min boundary hit no
    
    print('>> INFO >> TEST 2 >> rboundary__check_min 25')
    ret_hit_exp = False
    ret_exit_exp = False
    ret_cancel_exp = False
    
    ret_hit, ret_exit, ret_cancel, ret_price = rboundary__check_min(90000)
    if ret_hit == ret_hit_exp and ret_exit == ret_exit_exp and ret_cancel == ret_cancel_exp:
        print('>> INFO >> TEST 2 >> rboundary__check_min >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
    else:
        print('** ERROR >> TEST 2 >> rboundary__check_min >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
        sys.exit(1)
        
    ####################################################################
    ## test 2 min boundary hit yes
    
    print('>> INFO >> TEST 2 >> rboundary__check_min 24')
    ret_hit_exp = True
    ret_exit_exp = False
    ret_cancel_exp = True
    
    ret_hit, ret_exit, ret_cancel, ret_price = rboundary__check_min(8999)
    if ret_hit == ret_hit_exp and ret_exit == ret_exit_exp and ret_cancel == ret_cancel_exp:
        print('>> INFO >> TEST 2 >> rboundary__check_min >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
    else:
        print('** ERROR >> TEST 2 >> rboundary__check_min >> ret_hit, ret_exit, ret_cancel {},{},{}'.format(ret_hit, ret_exit, ret_cancel))
        sys.exit(1)
        
    ####################################################################
    ## test 2 price recompute
    
    print('>> INFO >> TEST 307 >> rboundary__check(700)')
    ret_hit, ret_exit, ret_cancel, ret_price = rboundary__check(70000)
    if ret_price == 30000:
        print('>> INFO >> TEST 310 >> rboundary__check(1) >> {} OK'.format(ret_price))
    else:
        print('>> ERROR >> TEST 312 >> rboundary__check(1) >> {}'.format(ret_price))
        sys.exit(1)
        
    print('>> INFO >> TEST 315 >> rboundary__check(2000+1)')
    ret_hit, ret_exit, ret_cancel, ret_price = rboundary__check(2000+1)
    if ret_price == 9000:
        print('>> INFO >> TEST 318 >> rboundary__check(20) >> {} OK'.format(ret_price))
    else:
        print('>> ERROR >> TEST 319 >> rboundary__check(20) >> {}'.format(ret_price))
        sys.exit(1)
