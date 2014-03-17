from zope.i18nmessageid import MessageFactory
from AccessControl import ModuleSecurityInfo, allow_type, allow_class
from Products.PythonScripts.Utility import allow_module

MessageFactory = MessageFactory('collective.auditlog')

from collective.auditlog.functionality import AuditLogTest, AuditLogChecker

allow_module('collective.auditlog.functionality')
ModuleSecurityInfo('collective.auditlog.functionality').declarePublic(
    'AuditLogTest', 'AuditLogChecker')

allow_class(AuditLogTest)
allow_class(AuditLogChecker)
allow_type(type(AuditLogTest.testingActions))
allow_type(type(AuditLogChecker.checkAction))


allow_module('collective.auditlog.async')
ModuleSecurityInfo('collective.auditlog.async').declarePublic('queueJob')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
