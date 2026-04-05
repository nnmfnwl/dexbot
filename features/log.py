#!/usr/bin/python3

# logger functionality

import time

from inspect import getframeinfo, stack
import os

import features.glob as glob
c = glob.c
s = glob.s
d = glob.d

# pre-configuration  initialization
def log__init_preconfig__():
    
    # static boundary asset
    c.log__action = True
    c.log__info = True
    c.log__debug = True
    c.log__hint = True
    
    c.log__fatal = True
    c.log__error = True
    c.log__warning = True

log__init_preconfig__()

# log action message
def LOG_ACTION(message, prefix = ""):
    
    if c.log__action:
        caller = getframeinfo(stack()[1][0]) # <-- stack()[1][0] for next caller line
        print("{}^^^^ ACTION {}:{} >> {}".format(prefix, os.path.basename(caller.filename), caller.lineno, message))

# log info message
def LOG_INFO(message, prefix = ""):
    
    if c.log__info:
        caller = getframeinfo(stack()[1][0]) # <-- stack()[1][0] for next caller line
        print("{}>>>> INFO {}:{} >> {}".format(prefix, os.path.basename(caller.filename), caller.lineno, message))

# log info message
def LOG_DEBUG(message, prefix = ""):
    
    if c.log__debug:
        caller = getframeinfo(stack()[1][0]) # <-- stack()[1][0] for next caller line
        print("{}---- DEBUG {}:{} >> {}".format(prefix, os.path.basename(caller.filename), caller.lineno, message))

# log info message
def LOG_HINT(message, prefix = ""):
    
    if c.log__hint:
        caller = getframeinfo(stack()[1][0]) # <-- stack()[1][0] for next caller line
        print("{}++++ HINT {}:{} >> {}".format(prefix, os.path.basename(caller.filename), caller.lineno, message))

# log fatal message
def LOG_FATAL(message, prefix = ""):
    
    if c.log__fatal:
        caller = getframeinfo(stack()[1][0]) # <-- stack()[1][0] for next caller line
        print("{}**** FATAL {}:{} >> {}".format(prefix, os.path.basename(caller.filename), caller.lineno, message))

# log error message
def LOG_ERROR(message, prefix = ""):
    
    if c.log__error:
        caller = getframeinfo(stack()[1][0]) # <-- stack()[1][0] for next caller line
        print("{}**** ERROR {}:{} >> {}".format(prefix, os.path.basename(caller.filename), caller.lineno, message))

# log warning message
def LOG_WARNING(message, prefix = ""):
    
    if c.log__warning:
        caller = getframeinfo(stack()[1][0]) # <-- stack()[1][0] for next caller line
        print("{}#### WARNING {}:{} >> {}".format(prefix, os.path.basename(caller.filename), caller.lineno, message))

