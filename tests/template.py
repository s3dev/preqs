#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:Purpose:   Testing module for the ``module`` module.

:Platform:  Linux/Windows | Python 3.6+
:Developer: J Berendt
:Email:     jeremy.berendt@rolls-royce.com

:Comments:  n/a

"""

try:
    from .base import TestBase
    from .testlibs import msgs
except ImportError:
    from base import TestBase
    from testlibs import msgs
# TestBase must be imported before <lib>.
# locals import here ...


class TestModule(TestBase):
    """Testing class used to test the ``module`` module."""

    _MSG1 = msgs.templates.not_as_expected.general

    @classmethod
    def setUpClass(cls):
        """Run this method at the start of all tests in this module.

        :Tasks:

            - Print the start of test message.

        """
        msgs.startoftest.message(module_name='')

    # @classmethod
    # def tearDownClass(cls):
    #     """Run this method at the end of all tests in this module.

    #     :Tasks:

    #         - ...

    #     """
    #     pass

    # def setUp(self):
    #     """Run this method at the start of *each* test.

    #     :Tasks:

    #         - ...

    #     """
    #     pass

    # def tearDown(self):
    #     """Run this method at the end of *each* test.

    #     :Tasks:

    #         - ...

    #     """
    #     pass

    def test01__methodname(self):
        """Test the ``<method>`` method.

        :Test:
            - < How this test operates. >

        """
        # inp = []
        # exp = []
        # for i, e in zip(inp, exp):
            # test = <method_call>(i)
            # utilities.assert_true(expected=e, test=test, msg=self._MSG1)
