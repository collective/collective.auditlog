from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


EVENT_TYPES = [
    (
        "Products.CMFCore.interfaces.IActionSucceededEvent",
        "A workflow action succeeded",
    ),
    (
        "plone.app.iterate.interfaces.IBeforeCheckoutEvent",
        "An object has been checked out.",
    ),
    (
        "plone.app.iterate.interfaces.ICancelCheckoutEvent",
        "A working copy has been cancelled.",
    ),
    (
        "plone.app.iterate.interfaces.ICheckinEvent",
        "A working copy has been checked in.",
    ),
    (
        "zope.lifecycleevent.interfaces.IObjectMovedEvent",  # noqa for black
        "An object has been moved",
    ),
    (
        "zope.lifecycleevent.interfaces.IObjectRemovedEvent",
        "An object has been removed",
    ),
    (
        "zope.lifecycleevent.interfaces.IObjectModifiedEvent",
        "An object has been modified",
    ),
    (
        "zope.lifecycleevent.interfaces.IObjectAddedEvent",  # noqa for black
        "An object has been added",
    ),
    (
        "OFS.interfaces.IObjectClonedEvent",  # noqa for black
        "An object has been copied",
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


@provider(IVocabularyFactory)
def EventTypesVocabulary(context):
    """Event types which are available for audit logging.
    Override this vocabulary if you want to extend or replace it.
    """
    items = [SimpleTerm(value=e[0], title=e[1]) for e in EVENT_TYPES]
    return SimpleVocabulary(items)
