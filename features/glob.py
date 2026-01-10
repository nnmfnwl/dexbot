#!/usr/bin/python3

class GlobVars(): pass

def __init__():
    #global config variables
    global c
    c = GlobVars()
    #global static variables
    global s
    s = GlobVars()
    #global dynamic variables
    global d
    d = GlobVars()
    #global tool functions
    global t
    t = GlobVars()
    #init
    t.argparse_bool = argparse_bool

def argparse_bool(arg):
    if isinstance(arg, bool):
        return arg
    elif isinstance(arg, str):
        if arg.lower() in ['true', 'enabled', 'yes', '1']:
            return True
        else:
            return False
    else:
        return False

__init__()
