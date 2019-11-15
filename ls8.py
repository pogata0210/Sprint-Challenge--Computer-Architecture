# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 11:14:17 2019

@author: pablo
"""
"""Main."""

import sys
from cpu import *

if len(sys.argv) != 2:
    print("usage: simple.py <filename>", file=sys.stderr)
    sys.exit(1)

cpu = CPU()
cpu.load(sys.argv[1])
cpu.run()