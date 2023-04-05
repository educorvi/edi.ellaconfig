# -*- coding: utf-8 -*-
from edi.ellaconfig.testing import EDI_ELLACONFIG_INTEGRATION_TESTING  # noqa
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest


try:
    from plone.dexterity.schema import portalTypeToSchemaName
except ImportError:
    # Plone < 5
    from plone.dexterity.utils import portalTypeToSchemaName


class ServiceIntegrationTest(unittest.TestCase):

    layer = EDI_ELLACONFIG_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            'EllaKonfig',
            self.portal,
            'parent_container',
            title='Parent container',
        )
        self.parent = self.portal[parent_id]

    def test_ct_service_schema(self):
        fti = queryUtility(IDexterityFTI, name='Service')
        schema = fti.lookupSchema()
        schema_name = portalTypeToSchemaName('Service')
        self.assertEqual(schema_name, schema.getName())

    def test_ct_service_fti(self):
        fti = queryUtility(IDexterityFTI, name='Service')
        self.assertTrue(fti)

    def test_ct_service_factory(self):
        fti = queryUtility(IDexterityFTI, name='Service')
        factory = fti.factory
        obj = createObject(factory)


    def test_ct_service_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='Service',
            id='service',
        )


        parent = obj.__parent__
        self.assertIn('service', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('service', parent.objectIds())

    def test_ct_service_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Service')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )

    def test_ct_service_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Service')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'service_id',
            title='Service container',
         )
        self.parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type='Document',
                title='My Content',
            )
