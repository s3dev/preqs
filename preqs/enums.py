#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the project's enumerators.

:Platform:  Linux/Windows | Python 3.8+
:Developer: J Berendt
:Email:     development@s3dev.uk

"""

from enum import Enum


class ExCode(Enum):
    """Exit code enumerators."""

    # preqs.Requirements
    GEN_OK = 0
    ERR_EXIST = 10
    ERR_FILES = 20
    ERR_IMPTS = 30
    ERR_CLEAN = 40
    ERR_VERSN = 50
    ERR_WRITE = 60
    ERR_CKINV = 100  # Check: Invalid path
    ERR_INITL = 255

    # check.RequirementsCheck
    ECK_RCFNF = 201  # Requirements file not found error
    ECK_RCNRQ = 202  # Not a requirements.txt file
