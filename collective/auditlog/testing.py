# coding=utf-8
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.configuration import xmlconfig


try:
    from plone.testing import zope as zope_testing
except ImportError:
    from plone.testing import z2 as zope_testing


class AuditLog(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # load ZCML

        import plone.app.contenttypes

        xmlconfig.file(
            "configure.zcml", plone.app.contenttypes, context=configurationContext
        )

        import collective.auditlog

        xmlconfig.file(
            "configure.zcml", collective.auditlog, context=configurationContext
        )
        zope_testing.installProduct(app, "collective.auditlog")

        # no async for testing
        from collective.auditlog import async

        async.queue_job = False

    def setUpPloneSite(self, portal):
        # install into the Plone site
        applyProfile(portal, "plone.app.contenttypes:default")
        applyProfile(portal, "collective.auditlog:default")
        setRoles(portal, TEST_USER_ID, ("Member", "Manager"))


AuditLog_FIXTURE = AuditLog()
AuditLog_INTEGRATION_TESTING = IntegrationTesting(
    bases=(AuditLog_FIXTURE,), name="AuditLog:Integration"
)
AuditLog_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(AuditLog_FIXTURE,), name="AuditLog:Functional"
)
