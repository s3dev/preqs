#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:Purpose:   Testing module for the ``preqs`` module.

:Platform:  Linux/Windows | Python 3.6+
:Developer: J Berendt
:Email:     jeremy.berendt@rolls-royce.com

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
from preqs import preqs


class TestPreqs(TestBase):
    """Testing class used to test the ``preqs`` module."""

    _FN = 'requirements.txt'
    _MSG1 = msgs.templates.not_as_expected.general

    @classmethod
    def setUpClass(cls):
        """Run this method at the start of all tests in this module.

        :Tasks:

            - Print the start of test message.

        """
        msgs.startoftest.message(module_name='preqs')

    @classmethod
    def setUp(cls):
        """Tasks to perform at the start of each test."""
        cls.redirect_stderr_to_devnull()

    @classmethod
    def tearDown(cls):
        """Tasks to perform at the end of each test."""
        cls.restore_stderr()

    def test01a__run__no_imports(self):
        """Test the ``run`` method for a project with no imports.

        :Test:
            - Verify the exit code is as expected.
            - Verify the requirements file does not exist.

        """
        pkg = 'pkg0'
        with self.assertRaises(SystemExit) as cm:
            r = preqs.Requirements()
            r._args.PATH = os.path.join(self._DIR_RESC, pkg)
            r.run()
        with self.subTest('Exit code'):
            tst = cm.exception.code
            exp = 30
            self.assertEqual(exp, tst, msg=self._MSG1.format(exp, tst))
        with self.subTest('File not exist'):
            tst = os.path.exists(os.path.join(self._DIR_RESC, pkg, self._FN))
            exp = False
            self.assertEqual(tst, exp, msg=self._MSG1.format(exp, tst))

    def test01b__run__no_args(self):
        """Test the ``run`` method with no arguments.

        :Test:
            - Verify the exit code is as expected.
            - Verify the hash of the requirements file is as expected.

        """
        pkg = 'pkg1'
        with self.assertRaises(SystemExit) as cm:
            r = preqs.Requirements()
            r._args.PATH = os.path.join(self._DIR_RESC, pkg)
            r.run()
        with self.subTest('Exit code'):
            tst = cm.exception.code
            exp = 0
            self.assertEqual(exp, tst, msg=self._MSG1.format(exp, tst))
        with self.subTest('File hash'):
            tst = self.calc_file_hash(pkg=pkg)
            exp = '50f5706f5ccec946a2c6d1a7e1862c47'
            self.assertEqual(tst, exp, msg=self._MSG1.format(tst, exp))
        self.remove_requirements_file(pkg=pkg)

    def test01c__run__file_exists(self):
        """Test the ``run`` method where a requirements file exists.

        :Test:
            - Verify the exit code is as expected.

        """
        pkg = 'pkg2'
        with self.assertRaises(SystemExit) as cm:
            r = preqs.Requirements()
            r._args.PATH = os.path.join(self._DIR_RESC, pkg)
            r.run()
        with self.subTest('Exit code'):
            tst = cm.exception.code
            exp = 10
            self.assertEqual(exp, tst, msg=self._MSG1.format(exp, tst))

    def test01d__run__no_py_modules(self):
        """Test the ``run`` method for a project without Python modules.

        :Test:
            - Verify the exit code is as expected.

        """
        pkg = 'pkg3'
        with self.assertRaises(SystemExit) as cm:
            r = preqs.Requirements()
            r._args.PATH = os.path.join(self._DIR_RESC, pkg)
            r.run()
        with self.subTest('Exit code'):
            tst = cm.exception.code
            exp = 20
            self.assertEqual(exp, tst, msg=self._MSG1.format(exp, tst))

    def test01e__run__ignore_dirs(self):
        """Test the ``run`` method with the --ignore_dirs flag.

        :Test:
            - Verify the exit code is as expected.
            - Verify the hash of the requirements file is as expected.

        """
        pkg = 'pkg4'
        with self.assertRaises(SystemExit) as cm:
            r = preqs.Requirements()
            r._args.PATH = os.path.join(self._DIR_RESC, pkg)
            r._IGNORE_DIRS += [os.path.join(self._DIR_RESC, pkg, 'build'),
                               os.path.join(self._DIR_RESC, pkg, 'docs')]
            r.run()
        with self.subTest('Exit code'):
            tst = cm.exception.code
            exp = 0
            self.assertEqual(exp, tst, msg=self._MSG1.format(exp, tst))
        with self.subTest('File hash'):
            tst = self.calc_file_hash(pkg=pkg)
            exp = '8f13b4b6c61cdbe2acf7abd80e929335'
            self.assertEqual(exp, tst, msg=self._MSG1.format(exp, tst))
        self.remove_requirements_file(pkg=pkg)

    def test02a__debug(self):
        """Test the ``run`` method with the --debug flag.

        :Test:
            - Verify the exit code is as expected.

        """
        pkg = 'pkg3'
        with self.assertRaises(SystemExit) as cm:
            r = preqs.Requirements()
            r._args.PATH = os.path.join(self._DIR_RESC, pkg)
            r._args.debug = True
            r.run()
        with self.subTest('Exit code'):
            tst = cm.exception.code
            exp = 20
            self.assertEqual(exp, tst, msg=self._MSG1.format(exp, tst))

    def test03a__write__print(self):
        """Test the ``_write`` method with the --print flag.

        :Test:
            - Verify the expected output is included in the print.

        """
        reqs = [('thing1', '1.0.0'), ('thing2', '2.0.0'), ('thing3', '3.0.0')]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            r = preqs.Requirements()
            r._args.print = True
            r._reqs = reqs
            r._write()
        stdout = buf.getvalue().split('\n')
        for idx, req in enumerate(reqs):
            with self.subTest(f'{idx}: {req}'):
                self.assertIn(str(req), stdout[idx+3])


#%% Helpers

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
