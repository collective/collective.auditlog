# coding=utf-8
from collective.auditlog.action import AuditActionExecutor
from collective.auditlog.utils import addLogEntry
from collective.auditlog.utils import getObjectInfo
from collective.auditlog.utils import getSite
from collective.auditlog.utils import getUID
from importlib import import_module
from plone.app.contentrules import handlers as cr_handlers
from plone.app.discussion.interfaces import IComment
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import IContentish
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.interface import Interface
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent

import json


class IMissingInterface(Interface):
    pass


try:
    from Products.Archetypes.interfaces import IBaseObject
except ImportError:
    IBaseObject = IMissingInterface


try:
    from plone.app.contentrules.handlers import (
        execute_rules,
        execute,
        is_portal_factory,
    )
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


def execute_event(obj, event=None):
    if event is None:
        # ActionSuceededEvent does not send an object first
        event = obj
        obj = event.object
    executor = None
    for ev in get_automatic_events():
        if ev.providedBy(event) and obj is not None:
            executor = AuditActionExecutor(None, None, event)
            executor()
            break
    if executor is None:
        # plone sends some events twice, first wrapped. Ignore those.
        if getattr(event, "object", None) is not None:
            execute_rules(event)


def moved_event(event):
    # only execute moved event if it's not a added or removed event since
    # those are handled elsewhere and they base off of this event class
    if IObjectAddedEvent.providedBy(event) or IObjectRemovedEvent.providedBy(event):
        return

    obj = event.object
    if not (IContentish.providedBy(obj) or IComment.providedBy(obj)):
        return
    execute_event(obj, event)


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
            "IObjectInitializedEvent-audit-%s" % getUID(obj)
        ] = event
    elif IContentish.providedBy(obj) or IComment.providedBy(obj):
        execute_event(obj, event)
    else:
        return


def loggedout_event(event):
    obj = event.object
    data = {"info": "", "action": "logged out"}
    log_entry(obj, data)


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
        "IObjectInitializedEvent-audit-%s" % getUID(obj), None
    )
    if delayed_event is not None:
        cr_handlers._status.delayed_events[
            "IObjectInitializedEvent-audit-%s" % getUID(obj)
        ] = None
        execute_event(obj, delayed_event)


def get_automatic_events():
    events = []
    site = getSite()
    try:
        qi = site.portal_quickinstaller
        installed = qi.isProductInstalled("collective.auditlog")
    except AttributeError:
        installed = False
    if installed:
        try:
            registry = getUtility(IRegistry)
            key = "collective.auditlog.interfaces.IAuditLogSettings.automaticevents"
            automaticevents = registry[key]
            for ev in automaticevents:
                module, interface = ev.rsplit(".", 1)
                imported = import_module(module)
                automatic = getattr(imported, interface, None)
                if automatic is not None:
                    events.append(automatic)
        except ComponentLookupError:
            # no registry, no events
            pass
    return events


def log_entry(obj, data, request=None):
    data.update(getObjectInfo(obj, request=request))
    addLogEntry(obj, data)


def custom_event(event):
    obj = event.object
    request = getattr(event, "request", None)
    info = event.info
    if info:
        try:
            tmp = json.loads(info)  # noqa
        except ValueError:
            info = json.dumps({"info": info})

    data = {"info": event.info, "action": event.action}
    log_entry(obj, data, request)
