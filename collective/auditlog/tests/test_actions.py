# coding=utf-8
from Products.Archetypes.event import ObjectEditedEvent
from Products.Archetypes.event import ObjectInitializedEvent
from zope.lifecycleevent import ObjectCreatedEvent
from collective.auditlog.db import getSession
from collective.auditlog.models import Base
from collective.auditlog.models import LogEntry
from collective.auditlog.interfaces import IAuditLogSettings
from collective.auditlog.testing import AuditLog_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import setRoles, login
from plone.registry.interfaces import IRegistry
from tempfile import mkstemp
from zope.component import getUtility
from zope.event import notify
import os
import transaction
import unittest


class tempDb(object):

    registry_key = '{iface}.connectionstring'.format(
        iface=IAuditLogSettings.__identifier__
    )

    def __init__(self):
        _, self.tempfilename = mkstemp()

    def __enter__(self):
        self.registry = registry = getUtility(IRegistry)
        registry[self.registry_key] = u'sqlite:///%s' % (self.tempfilename)
        session = getSession()
        Base.metadata.create_all(session.bind.engine)

    def __exit__(self, type, value, traceback):
        os.remove(self.tempfilename)


class TestActions(unittest.TestCase):

    layer = AuditLog_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request'].clone()
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    @property
    def logs(self):
        return getSession().query(LogEntry).all()

    def create_page(self, title='Page'):
        ''' Create a page and return it
        '''
        obj_id = self.portal.invokeFactory(
            type_name="Document",
            id="page",
            title=title,
        )
        obj = self.portal[obj_id]
        try:
            # AT only
            self.portal.page.unmarkCreationFlag()
            notify(ObjectInitializedEvent(obj))
        except AttributeError:
            notify(ObjectCreatedEvent(obj))
        return obj

    def test_add(self):
        with tempDb():
            self.create_page()
            self.assertEqual(self.logs[-1].action, 'added')

    def test_unicode(self):
        with tempDb():
            self.create_page(title='Pàge')
            self.assertEqual(self.logs[-1].action, 'added')

    def test_edit(self):
        self.create_page()

        with tempDb():
            notify(ObjectEditedEvent(self.portal.page))
            self.assertEqual(self.logs[-1].action, 'modified')

    @unittest.skip("The ObjectModifiedEvent seems not to be fired")
    def test_moved(self):
        self.create_page()
        self.portal.invokeFactory(type_name="Folder", id="folder",
                                  Title="folder")
        with tempDb():
            # We need to commit here so that _p_jar isn't None and move
            # will work
            transaction.savepoint(optimistic=True)
            cd = self.portal.manage_cutObjects('page')
            self.portal.folder.manage_pasteObjects(cd)
            self.assertEqual(self.logs[-1].action, 'moved')

    def test_copied(self):
        self.create_page()
        self.portal.invokeFactory(
            type_name="Folder",
            id="folder",
            title="folder",
        )
        with tempDb():
            # We need to commit here so that _p_jar isn't None and move
            # will work
            transaction.savepoint(optimistic=True)
            cd = self.portal.manage_copyObjects('page')
            self.portal.folder.manage_pasteObjects(cd)
            self.assertEqual(self.logs[-1].action, 'copied')

    @unittest.skip("The ObjectModifiedEvent seems not to be fired")
    def test_rename(self):
        self.create_page()

        with tempDb():
            # We need to commit here so that _p_jar isn't None and move
            # will work
            transaction.savepoint(optimistic=True)
            self.portal.manage_renameObject('page', 'page2')
            self.assertEqual(self.logs[-1].action, 'rename')

    def test_delete(self):
        self.create_page()

        with tempDb():
            self.portal.manage_delObjects(['page'])
            self.assertEqual(self.logs[-1].action, 'removed')
