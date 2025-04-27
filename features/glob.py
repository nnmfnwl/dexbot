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

__init__()
