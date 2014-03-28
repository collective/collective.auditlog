from z3c.form import interfaces

from zope import schema
from zope.interface import Interface

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.auditlog')

class IAuditLogSettings(Interface):
    """Audit Log settings. This allows you to set the database connection string."""

    connectionstring = schema.TextLine(title=_(u"Audit Log Connection String"),
                                description=_(u"help_auditlog_connection",
                                        default=u"Enter the connection string for the database Audit Log is to write to. Must be a valid SQLAlchemy connection string."),
                                required=True,
                                default=u'sqlite:///:memory:',
    )

    trackworkingcopies = schema.Bool(title=_(u"Track Working Copy Activity?"),
				description=_(u"help_auditlog_trackworkingcopies",
					default=u"When checked AuditLog will track all actions to Working Copies. When unchecked, only cancel check out and check-in actions will be tracked."),
				required=False,
    )
