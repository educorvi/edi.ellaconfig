# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from edi.ellaconfig.testing import EDI_ELLACONFIG_INTEGRATION_TESTING  # noqa: E501
from plone import api
from plone.app.testing import setRoles, TEST_USER_ID

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that edi.ellaconfig is properly installed."""

    layer = EDI_ELLACONFIG_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if edi.ellaconfig is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'edi.ellaconfig'))

    def test_browserlayer(self):
        """Test that IEdiEllaconfigLayer is registered."""
        from edi.ellaconfig.interfaces import (
            IEdiEllaconfigLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IEdiEllaconfigLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = EDI_ELLACONFIG_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['edi.ellaconfig'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if edi.ellaconfig is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'edi.ellaconfig'))

    def test_browserlayer_removed(self):
        """Test that IEdiEllaconfigLayer is removed."""
        from edi.ellaconfig.interfaces import \
            IEdiEllaconfigLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            IEdiEllaconfigLayer,
            utils.registered_layers())
