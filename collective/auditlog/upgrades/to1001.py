from collective.auditlog.interfaces import IAuditLogSettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


def fix_registry_records(context):
    """Fix the registry records"""
    registry = getUtility(IRegistry)
    registry.registerInterface(IAuditLogSettings)
