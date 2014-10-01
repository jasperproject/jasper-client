#!/usr/bin/env python2
# -*- coding: utf-8-*-
# This file exists for backwards compatibility with older versions of jasper.
# It might be removed in future versions.
import os
import sys
import runpy
script_path = os.path.join(os.path.dirname(__file__), os.pardir, "jasper.py")
sys.path.insert(0, os.path.dirname(script_path))
runpy.run_path(script_path, run_name="__main__")
