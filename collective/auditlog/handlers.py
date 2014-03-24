from zope.component.hooks import getSite
from zope.lifecycleevent.interfaces import (
    IObjectRemovedEvent, IObjectAddedEvent, IObjectCopiedEvent)
from plone.app.discussion.interfaces import IComment
from Products.CMFCore.interfaces import IContentish
from collective.auditlog.utils import getUID
from plone.app.contentrules import handlers as cr_handlers
from Products.Archetypes.interfaces import IBaseObject

try:
    from plone.app.contentrules.handlers import (
        execute_rules, execute, is_portal_factory)
except ImportError:
    from Acquisition import aq_inner, aq_parent
    from plone.app.contentrules.handlers import execute, is_portal_factory
    # copied from plone.app.iterate 2.0:

    def execute_rules(event):
        """ When an action is invoked on an object,
        execute rules assigned to its parent.
        Base action executor handler """

        if is_portal_factory(event.object):
            return

        execute(aq_parent(aq_inner(event.object)), event)


def execute_event(event, object=None):
    site = getSite()
    try:
        qi = site.portal_quickinstaller
    except AttributeError:
        return
    if qi.isProductInstalled('collective.auditlog'):
        execute_rules(event)


def moved_event(event):
    # only execute moved event if it's not a added or removed event since
    # those are handled elsewhere and they base off of this event class
    if (IObjectAddedEvent.providedBy(event) or
            IObjectRemovedEvent.providedBy(event)):
        return

    obj = event.object
    if not (IContentish.providedBy(obj) or IComment.providedBy(obj)):
        return
    execute_event(event)


def created_event(event):
    obj = event.object

    if is_portal_factory(obj):
        return

    if IObjectCopiedEvent.providedBy(event):
        return  # ignore this event since we're listening to cloned instead
    # The object added event executes too early for Archetypes objects.
    # We need to delay execution until we receive a subsequent
    # IObjectInitializedEvent
    if IBaseObject.providedBy(obj):
        cr_handlers.init()
        cr_handlers._status.delayed_events[
            'IObjectInitializedEvent-audit-%s' % getUID(obj)] = event
    elif IContentish.providedBy(obj) or IComment.providedBy(obj):
        execute_event(event)
    else:
        return


def archetypes_initialized(event):
    """Pick up the delayed IObjectAddedEvent when an Archetypes object is
    initialised.
    """
    obj = event.object
    if is_portal_factory(obj):
        return

    if not IBaseObject.providedBy(obj):
        return

    cr_handlers.init()
    delayed_event = cr_handlers._status.delayed_events.get(
        'IObjectInitializedEvent-audit-%s' % getUID(obj), None)
    if delayed_event is not None:
        cr_handlers._status.delayed_events[
            'IObjectInitializedEvent-audit-%s' % getUID(obj)] = None
        execute_event(delayed_event)
