#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the requirements file checking
            functionality by reporting the results of version checks
            between the requirements file and the installed libraries.

            The version checker is invoked from the command line via the
            ``-c`` or ``--check`` arguments.

:Platform:  Linux/Windows | Python 3.8+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

"""
# pylint: disable=import-error

import logging
import os
import re
from importlib import metadata
from packaging.version import Version
# locals
from enums import ExCode

logger = logging.getLogger(__name__)


class RequirementCheck:
    """Compare requirements file versions against the installed versions.

    Args:
        path (str): Path of the requirements file to be checked. This
            should be the ``PATH`` argument from the argument parser.
            This path may contain the full path to the requirements file.

    :Checks:
        For each package listed in the ``requirements.txt`` file, check
        the version listed with the version installed, and report the
        findings.

        The ``Status`` field will show one of the following values,
        based on the version found in requirements, relative to the
        installed version:

            - **Same:**  The installed version is the same as the
                         requirements file’s version.
            - **Older:** The installed version is older than the
                         requirements file’s version.
            - **Newer:** The installed version is newer than the
                         requirements file’s version.
            - **Not installed:** The package is not installed.

    """

    def __init__(self, path: str) -> None:
        """RequirementCheck class initialiser."""
        self._path = path
        self._pkgs = []         # List of packages found in the requirements file.
        self._results = []      # List containing the results to be reported to the terminal.
        self._excode = ExCode.ERR_INITL

    @property
    def exit_code(self) -> int:
        """Accessor to this class' exit code."""
        return self._excode

    def check(self) -> bool:
        """Carry out requirements file checks.

        Returns:
            bool: True if the checks are carried out successfully,
            otherwise False.

        """
        self._path_exists()
        self._read()
        self._collect()
        self._report()
        self._excode = ExCode.GEN_OK

    def _report(self):  # pragma: nocover  # Not needed
        """Report the version compare findings to the terminal."""
        # pylint: disable=consider-using-f-string
        print('\n',
              '{:25}'.format('Name'),
              '{:15}'.format('Requirement'),
              '{:15}'.format('Installed'),
              'Status',
              '\n',
              '-'*65,
              sep='')
        for pkg, rvers, ivers, status in self._results:
            print(f'{pkg:25}',
                  f'{rvers:15}',
                  f'{ivers:15}',
                  status,
                  sep='')
        print()

    def _collect(self):
        """Collect the version from each listed installed library."""
        # rvers: requirements version
        # ivers: installed version
        for pkg, rvers in self._pkgs:
            try:
                ivers = metadata.version(pkg)
                if Version(ivers) == Version(rvers):
                    status = 'Same'
                elif Version(ivers) < Version(rvers):
                    status = 'Older'
                else:
                    status = 'Newer'
                self._results.append((pkg, rvers, ivers, status))
            except metadata.PackageNotFoundError:
                self._results.append((pkg, rvers, 'n/a', 'Not installed'))
        logger.debug('Results: %s', self._results)

    def _path_exists(self) -> None:
        """Verify the path to the requirements file exists.

        Raises:
            FileNotFoundError: Raised if the requirements file does not
            exist. This error is designed to be caught by the
            :meth:`preqs.Requirements.run` method.

            ValueError: Raised if the provided file is not a
            requirements.txt file.

        """
        if os.path.isdir(self._path):
            self._path = os.path.join(self._path, 'requirements.txt')
        if not os.path.exists(self._path):
            self._excode = ExCode.ECK_RCFNF
            raise FileNotFoundError(f'File not found: {self._path}')
        if os.path.basename(self._path) != 'requirements.txt':
            self._excode = ExCode.ECK_RCNRQ
            raise ValueError('File must be a requirements.txt file')

    def _read(self) -> None:
        """Read the requirements file.

        The results of the read are stored into the :attr:`_pkgs`
        attribute for later analysis.

        """
        # pylint: disable=unnecessary-lambda-assignment  # For clarity
        logger.debug('Reading requirements file: %s', self._path)
        filter_ = lambda x: x and not x.startswith('#')
        with open(self._path, 'r', encoding='utf-8') as f:
            _pkgs = list(filter(filter_, (line.strip() for line in f)))
        logger.debug('Contents of %s: %s',
                     self._path,
                     ''.join(map('\n\t - {}'.format, _pkgs)))
        # Split the 'package==0.0.7' entries into ('package', '0.0.7').
        rexp = re.compile('^(.*)[><=]+=(.*)$')
        _pkgs = list(map(lambda x: tuple(filter(None, rexp.split(x))), _pkgs))
        self._pkgs = _pkgs
