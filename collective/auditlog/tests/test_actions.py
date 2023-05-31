from collective.auditlog.db import getSession
from collective.auditlog.interfaces import IAuditLogSettings
from collective.auditlog.models import Base
from collective.auditlog.models import LogEntry
from collective.auditlog.testing import AuditLog_FUNCTIONAL_TESTING
from plone.app.contentrules.handlers import _status
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from tempfile import mkstemp
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectAddedEvent

import json
import os
import transaction
import unittest


class tempDb:
    registry_key = "{iface}.connectionstring".format(
        iface=IAuditLogSettings.__identifier__
    )
    session = None

    def __init__(self):
        _, self.tempfilename = mkstemp()

    @property
    def logs(self):
        return self.session.query(LogEntry).all()

    def __enter__(self):
        self.registry = registry = getUtility(IRegistry)
        registry[self.registry_key] = "sqlite:///%s" % (self.tempfilename)
        self.session = getSession()
        Base.metadata.create_all(self.session.bind.engine)
        return self

    def __exit__(self, type, value, traceback):
        os.remove(self.tempfilename)


class TestActions(unittest.TestCase):
    layer = AuditLog_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"].clone()
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        registry_key = "{iface}.automaticevents".format(
            iface=IAuditLogSettings.__identifier__
        )
        registry = getUtility(IRegistry)
        registry[registry_key] = [
            "OFS.interfaces.IObjectClonedEvent",
            "plone.app.iterate.interfaces.IBeforeCheckoutEvent",
            "plone.app.iterate.interfaces.ICancelCheckoutEvent",
            "plone.app.iterate.interfaces.ICheckinEvent",
            "Products.CMFCore.interfaces.IActionSucceededEvent",
            "zope.lifecycleevent.interfaces.IObjectAddedEvent",
            "zope.lifecycleevent.interfaces.IObjectModifiedEvent",
            "zope.lifecycleevent.interfaces.IObjectMovedEvent",
        ]

    def create_page(self, title="Page"):
        """Create a page and return it"""
        obj_id = self.portal.invokeFactory(
            "Document",
            id="page",
            title=title,
        )
        obj = self.portal[obj_id]
        notify(ObjectAddedEvent(obj))
        # We need to commit here so that _p_jar isn't None and move will work
        transaction.savepoint(optimistic=True)
        return obj

    def reset_rule_filter(self):
        """If we want to execute a rule multiple times in the same test
        we need to reset the rule filter, mocking a fresh request
        """
        _status.rule_filter.reset()

    def test_add(self):
        with tempDb() as db:
            self.create_page()
            self.assertEqual(db.logs[-1].action, "added")

    def test_unicode(self):
        with tempDb() as db:
            self.create_page(title="Pàge")
            self.assertEqual(db.logs[-1].action, "added")

    @unittest.skip("The ObjectModifiedEvent seems not to be fired")
    def test_moved(self):
        self.create_page()
        self.portal.invokeFactory("Folder", id="folder", Title="folder")
        with tempDb() as db:
            cd = self.portal.manage_cutObjects("page")
            self.portal.folder.manage_pasteObjects(cd)
            self.assertEqual(db.logs[-1].action, "moved")

    def test_copied(self):
        self.create_page()
        self.portal.invokeFactory(
            "Folder",
            id="folder",
            title="folder",
        )
        with tempDb() as db:
            cd = self.portal.manage_copyObjects("page")
            self.portal.folder.manage_pasteObjects(cd)
            self.assertEqual(db.logs[-1].action, "copied")

    @unittest.skip("The ObjectModifiedEvent seems not to be fired")
    def test_rename(self):
        self.create_page()

        with tempDb() as db:
            self.portal.manage_renameObject("page", "page2")
            self.assertEqual(db.logs[-1].action, "rename")

    def test_delete(self):
        self.create_page()

        with tempDb() as db:
            self.portal.manage_delObjects(["page"])
            self.assertEqual(db.logs[-1].action, "removed")

    def test_transition(self):
        self.create_page()
        pw = getToolByName(self.portal, "portal_workflow")
        with tempDb() as db:
            # publish and ...
            pw.doActionFor(
                self.portal.page,
                "publish",
            )
            self.assertEqual(db.logs[-1].action, "workflow")
            info = json.loads(db.logs[-1].info)
            self.assertEqual(info["transition"], "publish")
            self.assertEqual(info["comments"], "")

            self.reset_rule_filter()
            # ... retract the test page (adding a comment)
            pw.doActionFor(self.portal.page, "retract", comment="I've been commented ♥")
            self.assertEqual(db.logs[-1].action, "workflow")
            info = json.loads(db.logs[-1].info)
            self.assertEqual(info["transition"], "retract")
            self.assertEqual(info["comments"], "I've been commented \u2665")
