#!/usr/bin/env python3

import time
import random
import argparse
import sys
import logging
from utils import dxbottools
from utils import dxsettings

from tests.unit_test_sboundary import unit_test__sboundary
from tests.unit_test_rboundary import unit_test__rboundary

# main function
if __name__ == '__main__':
    
    unit_test__sboundary()
    unit_test__rboundary()
