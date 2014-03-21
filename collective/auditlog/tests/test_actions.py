from zope.event import notify
import unittest
from collective.auditlog.testing import AuditLog_INTEGRATION_TESTING
from Products.Archetypes.event import ObjectEditedEvent
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from tempfile import mkstemp
import os
from collective.auditlog import db
from collective.auditlog.models import LogEntry
from collective.auditlog.interfaces import DB_STRING_KEY
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import setRoles, login
import transaction
from Products.Archetypes.event import ObjectInitializedEvent


class tempDb(object):

    def __init__(self):
        _, self.tempfilename = mkstemp()

    def __enter__(self):
        self.registry = registry = getUtility(IRegistry)
        registry[DB_STRING_KEY] = u'sqlite:///%s' % (
            self.tempfilename)

    def __exit__(self, type, value, traceback):
        os.remove(self.tempfilename)


class TestActions(unittest.TestCase):

    layer = AuditLog_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_add(self):
        with tempDb():
            self.portal.invokeFactory(type_name="Document", id="page",
                                      Title="Page")
            self.portal.page.unmarkCreationFlag()
            notify(ObjectInitializedEvent(self.portal.page))
            self.assertEqual(len(db.getSession()().query(LogEntry).all()), 1)
            self.assertEqual(db.getSession()().query(LogEntry).all()[0].action,
                             'added')

    def test_edit(self):
        self.portal.invokeFactory(type_name="Document", id="page",
                                  Title="Page")
        self.portal.page.unmarkCreationFlag()

        with tempDb():
            notify(ObjectEditedEvent(self.portal.page))
            self.assertEqual(len(db.getSession()().query(LogEntry).all()), 1)
            self.assertEqual(db.getSession()().query(LogEntry).all()[0].action,
                             'modified')

    def test_moved(self):
        self.portal.invokeFactory(type_name="Document", id="page",
                                  Title="Page")
        self.portal.page.unmarkCreationFlag()
        self.portal.invokeFactory(type_name="Folder", id="folder",
                                  Title="folder")
        with tempDb():
            # We need to commit here so that _p_jar isn't None and move
            # will work
            transaction.savepoint(optimistic=True)
            cd = self.portal.manage_cutObjects('page')
            self.portal.folder.manage_pasteObjects(cd)
            self.assertEqual(len(db.getSession()().query(LogEntry).all()), 1)
            self.assertEqual(db.getSession()().query(LogEntry).all()[0].action,
                             'moved')

    def test_copied(self):
        self.portal.invokeFactory(type_name="Document", id="page",
                                  Title="Page")
        self.portal.page.unmarkCreationFlag()
        self.portal.invokeFactory(type_name="Folder", id="folder",
                                  Title="folder")
        with tempDb():
            # We need to commit here so that _p_jar isn't None and move
            # will work
            transaction.savepoint(optimistic=True)
            cd = self.portal.manage_copyObjects('page')
            self.portal.folder.manage_pasteObjects(cd)
            self.assertEqual(len(db.getSession()().query(LogEntry).all()), 1)
            self.assertEqual(db.getSession()().query(LogEntry).all()[0].action,
                             'copied')

    def test_rename(self):
        self.portal.invokeFactory(type_name="Document", id="page",
                                  Title="Page")
        self.portal.page.unmarkCreationFlag()
        with tempDb():
            # We need to commit here so that _p_jar isn't None and move
            # will work
            transaction.savepoint(optimistic=True)
            self.portal.manage_renameObject('page', 'page2')
            self.assertEqual(len(db.getSession()().query(LogEntry).all()), 1)
            self.assertEqual(db.getSession()().query(LogEntry).all()[0].action,
                             'rename')

    def test_delete(self):
        self.portal.invokeFactory(type_name="Document", id="page",
                                  Title="Page")
        self.portal.page.unmarkCreationFlag()

        with tempDb():
            self.portal.manage_delObjects(['page'])
            self.assertEqual(len(db.getSession()().query(LogEntry).all()), 1)
            self.assertEqual(db.getSession()().query(LogEntry).all()[0].action,
                             'removed')
