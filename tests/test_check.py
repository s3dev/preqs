#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:Purpose:   Testing module for the ``check`` module.

:Platform:  Linux/Windows | Python 3.8+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

"""
# pylint: disable=arguments-differ
# pylint: disable=protected-access
# pylint: disable=wrong-import-order

import contextlib
import hashlib
import io
import os
try:  # pragma: nocover
    from .base import TestBase
    from .testlibs import msgs
except ImportError:
    from base import TestBase
    from testlibs import msgs
# TestBase must be imported before preqs.
from preqs.check import RequirementCheck
from enums import ExCode


class TestCheck(TestBase):
    """Testing class used to test the ``check`` module."""

    _FN = 'requirements.txt'
    _MSG1 = msgs.templates.not_as_expected.general

    @classmethod
    def setUpClass(cls):
        """Run this method at the start of all tests in this module.

        :Tasks:

            - Print the start of test message.

        """
        msgs.startoftest.message(module_name='check')

    @classmethod
    def setUp(cls):
        """Tasks to perform at the start of each test."""
        cls.redirect_stderr_to_devnull()

    @classmethod
    def tearDown(cls):
        """Tasks to perform at the end of each test."""
        cls.restore_stderr()

    def test00a__check(self):
        """Test the ``check`` method via black box.

        :Test:
            - Black-box test the ``check`` method and verify the MD5 hash
              of the reported output is as expected.

        """
        buff = io.StringIO()
        pkg = 'pkg5'
        with contextlib.redirect_stdout(buff):
            rc = RequirementCheck(path=os.path.join(self._DIR_RESC, pkg))
            rc.check()
        text = buff.getvalue()
        tst = hashlib.md5(text.encode()).hexdigest()
        exp = '7c5fc8de8cafd79ae84b7b17276fa4c0'
        self.assertEqual(exp, tst)

    def test01a__path_exists(self):
        """Test the ``_path_exists`` method.

        :Test:
            - Verify the exit code is as expected.
            - Verify the appropriate error is raised (if applicable).

        """
        pkg = 'pkg5'
        rc = RequirementCheck(path=os.path.join(self._DIR_RESC, pkg))
        rc._path_exists()
        tst = rc.exit_code
        exp = ExCode.ERR_INITL
        self.assertEqual(exp, tst)

    def test01b__path_exists__not_exist(self):
        """Test the ``_path_exists`` method; file does not exist.

        :Test:
            - Verify the exit code is as expected.
            - Verify the appropriate error is raised (if applicable).

        """
        pkg = 'pkg1'
        rc = RequirementCheck(path=os.path.join(self._DIR_RESC, pkg))
        with self.assertRaises(FileNotFoundError):
            rc._path_exists()
        with self.subTest('Exit code'):
            tst = rc.exit_code
            exp = ExCode.ECK_RCFNF
            self.assertEqual(exp, tst)

    def test01c__path_exists__not_req_file(self):
        """Test the ``_path_exists`` method; not a requirements file.

        :Test:
            - Verify the exit code is as expected.
            - Verify the appropriate error is raised (if applicable).

        """
        pkg = 'pkg5'
        rc = RequirementCheck(path=os.path.join(self._DIR_RESC, pkg, 'mod0.py'))
        with self.assertRaises(ValueError):
            rc._path_exists()
        with self.subTest('Exit code'):
            tst = rc.exit_code
            exp = ExCode.ECK_RCNRQ
            self.assertEqual(exp, tst)

    def test02a__read(self):
        """Test the ``_read`` method.

        :Test:
            - Verify the requirements file is read and parsed as
              expected.

        """
        pkg = 'pkg5'
        rc = RequirementCheck(path=os.path.join(self._DIR_RESC, pkg, 'requirements.txt'))
        rc._read()
        exp = [('coverage', '7.8.0'),
               ('psutil', '6.1.0'),
               ('pylint', '3.3.7'),
               ('six', '1.17.0'),
               ('tomlkit', '0.13.2')]
        tst = rc._pkgs
        self.assertEqual(exp, tst)

    def test03a__collect__same(self):
        """Test the ``_collect`` method; results all the same.

        :Test:
            - Verify the collected results are as expected.

        """
        pkg = 'pkg5'
        rc = RequirementCheck(path=os.path.join(self._DIR_RESC, pkg, 'requirements.txt'))
        rc._read()
        rc._collect()
        exp = [('coverage', '7.8.0', '7.8.0', 'Same'),
               ('psutil', '6.1.0', '6.1.0', 'Same'),
               ('pylint', '3.3.7', '3.3.7', 'Same'),
               ('six', '1.17.0', '1.17.0', 'Same'),
               ('tomlkit', '0.13.2', '0.13.2', 'Same')]
        tst = rc._results
        self.assertEqual(exp, tst)

    def test03b__collect__mix(self):
        """Test the ``_collect`` method; mixed results.

        :Test:
            - Hack different versions into the ``_pkgs`` attribute to
              test the result of the collection.
            - Verify the collected results are as expected.

        """
        pkg = 'pkg5'
        rc = RequirementCheck(path=os.path.join(self._DIR_RESC, pkg, 'requirements.txt'))
        rc._pkgs = [('coverage', '7.8.0'),   # Same
                    ('psutil', '99.1.0'),     # Older
                    ('pylint', '99.3.7'),     # Older
                    ('six', '0.17.0'),       # Newer
                    ('tomlkit', '0.0.2'),   # Newer
                    ('spamneggs', '0.0.7')]  # Not installed
        rc._collect()
        exp = [('coverage', '7.8.0', '7.8.0', 'Same'),
               ('psutil', '99.1.0', '6.1.0', 'Older'),
               ('pylint', '99.3.7', '3.3.7', 'Older'),
               ('six', '0.17.0', '1.17.0', 'Newer'),
               ('tomlkit', '0.0.2', '0.13.2', 'Newer'),
               ('spamneggs', '0.0.7', 'n/a', 'Not installed')]
        tst = rc._results
        self.assertEqual(exp, tst)
