from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.interface.declarations import implementer
from zope.interface.interface import Attribute
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


_ = MessageFactory("collective.auditlog")

EVENT_TYPES = [
    (
        "plone.app.iterate.interfaces.ICheckinEvent",
        "A working copy has been checked in.",
    ),
    (
        "plone.app.iterate.interfaces.IBeforeCheckoutEvent",
        "An object has been checked out.",
    ),
    (
        "plone.app.iterate.interfaces.ICancelCheckoutEvent",
        "A working copy has been cancelled.",
    ),
    ("zope.lifecycleevent.interfaces.IObjectMovedEvent", "An object has been moved"),
    ("zope.lifecycleevent.interfaces.IObjectAddedEvent", "An object has been added"),
    (
        "zope.lifecycleevent.interfaces.IObjectModifiedEvent",
        "An object has been modified",
    ),
    (
        "zope.lifecycleevent.interfaces.IObjectRemovedEvent",
        "An object has been removed",
    ),
    ("OFS.interfaces.IObjectClonedEvent", "An object has been copied"),
    (
        "Products.CMFCore.interfaces.IActionSucceededEvent",
        "A workflow action succeeded",
    ),
    (
        "Products.PluggableAuthService.interfaces.events.IUserLoggedInEvent",
        "A user logged in",
    ),
    (
        "Products.PluggableAuthService.interfaces.events.IUserLoggedOutEvent",
        "A user logged out",
    ),
]

EVENT_TYPES_VOCAB = [SimpleTerm(e[0], e[0], e[1]) for e in EVENT_TYPES]


class IAuditLogSettings(Interface):
    """Audit Log settings.
    This allows you to set the database connection string.
    """

    storage = schema.Choice(
        title=_(u"Log storage"),
        description=_(
            u"help_auditlog_storage",
            default=(
                u"Audit Log is designed for use with a SQL database, "
                u"but the data can be stored in the ZODB catalog for "
                u"allowing audit log searches with catalog indexes."
            ),
        ),
        required=True,
        default="sql",
        values=("sql", "sql+zodb"),
    )

    connectionstring = schema.TextLine(
        title=_(u"Audit Log Connection String"),
        description=_(
            u"help_auditlog_connection",
            default=(
                u"Enter the connection string for the database Audit Log "
                u"is to write to. "
                u"Must be a valid SQLAlchemy connection string."
            ),
        ),
        required=True,
        default=u"sqlite:///:memory:",
    )

    connectionparameters = schema.TextLine(
        title=_(u"Audit Log Connection Parameters"),
        description=_(
            u"help_auditlog_connection_parameteers",
            default=(
                u"Enter the connection parametes in a json form. "
                u'E.g.: \'{"pool_recycle": 3600, "echo": true}\' '
            ),
        ),
        required=True,
        default=u"",
    )

    trackworkingcopies = schema.Bool(
        title=_(u"Track Working Copy Activity?"),
        description=_(
            u"help_auditlog_trackworkingcopies",
            default=(
                u"When checked AuditLog will track all actions "
                u"to Working Copies. "
                u"When unchecked, only cancel check out and check-in actions "
                u"will be tracked."
            ),
        ),
        required=False,
    )

    automaticevents = schema.List(
        title=_(u"Trigger Without Content Rule"),
        description=_(
            u"help_auditlog_automaticevents",
            default=(
                u"The selected events will not require a content rule "
                u"to trigger them, so all instances will be logged."
            ),
        ),
        default=[],
        value_type=schema.Choice(vocabulary=SimpleVocabulary(EVENT_TYPES_VOCAB)),
    )


class IAuditableActionPerformedEvent(Interface):
    """An event for signaling auditable actions."""

    object = Attribute("The subject of the event.")
    request = Attribute("The current request.")
    action = Attribute("A title for the performed action.")
    note = Attribute("Additional information for the action.")


@implementer(IAuditableActionPerformedEvent)
class AuditableActionPerformedEvent(object):
    def __init__(self, object, request, action, info=None):
        self.object = object
        self.request = request
        self.action = action
        self.info = info


class IBeforeStoreAuditlogEntryEvent(Interface):
    """ Event fired before storing an entry into the auditlog"""

    object = Attribute("The subject of the event.")
    data = Attribute("The data stored in the log")


@implementer(IBeforeStoreAuditlogEntryEvent)
class BeforeStoreAuditlogEntryEvent(object):
    def __init__(self, object, data):
        self.object = object
        self.data = data
