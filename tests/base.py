#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the superclass which is to be inherited
            by the test-specific modules.

:Platform:  Linux/Windows | Python 3.6+
:Developer: J Berendt
:Email:     development@s3dev.uk

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

import hashlib
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

    def calc_file_hash(self, pkg: str) -> str:
        """Calculate an MD5 hash against a requirements file.

        As each file has a timestamp at the end, the last line of the
        file is excluded from the hash.

        Args:
            pkg (str): Name of the package used for the test.

        Returns:
            str: An MD5 hash of the requirements file, except the final
            line containing the timestamp.

        """
        with open(os.path.join(self._DIR_RESC, pkg, self._FN), encoding='utf-8') as f:
            text = f.readlines()
        return hashlib.md5(''.join(text[:-1]).encode()).hexdigest()

    def remove_requirements_file(self, pkg: str):
        """Remove the requirements file from the given package.

        Args:
            pkg (str): Name of the package from which the file is to be
                removed.

        """
        path = os.path.join(self._DIR_RESC, pkg, 'requirements.txt')
        if os.path.exists(path):
            os.remove(path)
