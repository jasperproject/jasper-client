#!/usr/bin/env python2
# -*- coding: utf-8-*-
import unittest
from client import diagnose


class TestDiagnose(unittest.TestCase):
    def testPythonImportCheck(self):
        # This a python stdlib module that definitely exists
        self.assertTrue(diagnose.check_python_import("os"))
        # I sincerly hope nobody will ever create a package with that name
        self.assertFalse(diagnose.check_python_import("nonexistant_package"))
