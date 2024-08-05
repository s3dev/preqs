#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the superclass which is to be inherited
            by the test-specific modules.

:Platform:  Linux/Windows | Python 3.6+
:Developer: J Berendt
:Email:     jeremy.berendt@rolls-royce.com

:Example:
    Example code use.

    Run all tests via the shell script::

        $ ./run.sh

    Run all tests using unittest::

        $ python -m unittest discover

    Run a single test::

        $ python -m unittest test_name.py

"""
# pylint: disable=wrong-import-position

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import unittest


class TestBase(unittest.TestCase):
    """Private generalised base-testing class.

    This class is designed to be inherited by each test-specific class.

    """
    # Allow room for the side comments.
    # pylint: disable=line-too-long

    _DIR_PROJ_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    _DIR_TEST_ROOT = os.path.join(_DIR_PROJ_ROOT, 'tests')
    _DIR_RESC = os.path.join(_DIR_TEST_ROOT, 'resources')   # Path to the test resources directory.
    _DIR_VER_DATA = os.path.join(_DIR_RESC, 'data')         # Path to the verification data directory.

    @classmethod
    def setUpClass(cls):
        """Run this method at the start of all tests in this module.

        :Tasks:

            - Ignore the listed warnings.

        """

    @classmethod
    def tearDownClass(cls):
        """Teardown the testing class once all tests are complete."""

    @classmethod
    def redirect_stderr_to_devnull(cls):
        """Redirect STDERR to suppress output while testing."""
        # pylint: disable=consider-using-with
        # pylint: disable=unspecified-encoding
        cls._stderr = sys.stderr
        cls._fstderr = open(os.devnull, 'w')
        sys.stderr = cls._fstderr

    @classmethod
    def restore_stderr(cls):
        """Restore STDERR to reinstate output."""
        cls._fstderr.close()
        sys.stderr = cls._stderr
