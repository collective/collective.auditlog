# coding=utf-8
from collective.auditlog.testing import AuditLog_INTEGRATION_TESTING
from collective.auditlog import utils

import unittest


class TestUtils(unittest.TestCase):

    layer = AuditLog_INTEGRATION_TESTING

    def test_objectinfo(self):
        info = utils.getObjectInfo(
            type(
                "TestClass",
                (object,),
                {
                    "getPhysicalPath": lambda _self: ("", "path", "to", "ob"),
                    "title": "test",
                    "portal_type": "Test Type",
                    "UID": "123",
                },
            )()
        )
        self.assertIsNotNone(info["performed_on"])
        self.assertEqual(info["path"], "/path/to/ob")
        self.assertEqual(info["type"], "Test Type")
        self.assertEqual(info["title"], "test")
        self.assertEqual(info["uid"], "123")
        self.assertEqual(info["user"], "test-user")

    def test_objectinfo_none(self):
        info = utils.getObjectInfo(type("TestClass", (object,), {},)())
        self.assertEqual(
            info["type"],
            "collective.auditlog.tests.test_utils.TestClass (Python class)",
        )

    def test_objectinfo_id(self):
        info = utils.getObjectInfo(type("TestClass", (object,), {"id": "test id"})())
        self.assertEqual(info["path"], "test id (id)")
        self.assertEqual(info["title"], "test id (id)")

    def test_objectinfo_uid(self):
        info = utils.getObjectInfo(
            type("TestClass", (object,), {"UID": "test UID attr"})()
        )
        self.assertEqual(info["uid"], "test UID attr")

        info = utils.getObjectInfo(
            type("TestClass", (object,), {"UID": "test UID callable"})()
        )
        self.assertEqual(info["uid"], "test UID callable")

    def test_objectinfo_title(self):
        info = utils.getObjectInfo(
            type("TestClass", (object,), {"title": "test title attribute"})()
        )
        self.assertEqual(info["title"], "test title attribute")

        info = utils.getObjectInfo(
            type("TestClass", (object,), {"title": "test Title attribute"})()
        )
        self.assertEqual(info["title"], "test Title attribute")

        info = utils.getObjectInfo(
            type("TestClass", (object,), {"title": "test title callable"})()
        )
        self.assertEqual(info["title"], "test title callable")

        info = utils.getObjectInfo(
            type("TestClass", (object,), {"title": "test Title callable"})()
        )
        self.assertEqual(info["title"], "test Title callable")

        info = utils.getObjectInfo(
            type("TestClass", (object,), {"id": "test no title but id"})()
        )
        self.assertEqual(info["title"], "test no title but id (id)")
