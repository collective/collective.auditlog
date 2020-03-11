# coding=utf-8
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID


class AuditLog(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import plone.app.contenttypes
        import collective.auditlog
        import collective.auditlog.asyncqueue

        self.loadZCML(package=plone.app.contenttypes)
        self.loadZCML(package=collective.auditlog)

        collective.auditlog.asyncqueue.queue_job = False

    def setUpPloneSite(self, portal):
        applyProfile(portal, "plone.app.contenttypes:default")
        applyProfile(portal, "collective.auditlog:default")
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")
        setRoles(portal, TEST_USER_ID, ("Member", "Manager"))


AuditLog_FIXTURE = AuditLog()
AuditLog_INTEGRATION_TESTING = IntegrationTesting(
    bases=(AuditLog_FIXTURE,), name="AuditLog:Integration"
)
AuditLog_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(AuditLog_FIXTURE,), name="AuditLog:Functional"
)
