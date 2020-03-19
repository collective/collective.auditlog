# coding=utf-8
from collective.auditlog.utils import addLogEntry
from collective.auditlog.utils import getObjectInfo
from OFS.interfaces import IObjectClonedEvent
from OFS.SimpleItem import SimpleItem
from plone.app.contentrules.browser.formhelper import AddForm
from plone.app.contentrules.browser.formhelper import EditForm
from plone.app.iterate.interfaces import IBeforeCheckoutEvent
from plone.app.iterate.interfaces import ICancelCheckoutEvent
from plone.app.iterate.interfaces import ICheckinEvent
from plone.app.iterate.interfaces import IWorkingCopy
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleElementData
from plone.contentrules.rule.rule import RuleExecutable
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.PluggableAuthService.interfaces.events import IUserLoggedInEvent
from Products.PluggableAuthService.interfaces.events import IUserLoggedOutEvent
from zope.component import adapter
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.interface import Interface
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectMovedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent

import inspect
import json
import logging


try:
    from plone.app.iterate.relation import WorkingCopyRelation
except ImportError:
    # Import will fail if we do not have Products.Archetypes
    WorkingCopyRelation = None


logger = logging.getLogger("collective.auditlog")


class IAuditAction(Interface):
    pass


@implementer(IAuditAction, IRuleElementData)
class AuditAction(SimpleItem):
    element = "plone.actions.Audit"
    summary = u"Audit"


@implementer(IExecutable)
@adapter(Interface, IAuditAction, Interface)
class AuditActionExecutor(object):
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    @property
    def request(self):
        """Try to get a request
        """
        return getRequest()

    @property
    @memoize
    def rule(self):
        """ Check up the stack the rule that invoked this action
        """
        # start higher in the stack
        frame = inspect.currentframe().f_back.f_back
        while frame:
            rule = frame.f_locals.get("self", None)
            if isinstance(rule, RuleExecutable):
                return rule
            frame = frame.f_back
        return None

    @property
    def can_execute(self):
        environ = getattr(self.request, "environ", {})
        if environ.get("disable.auditlog", False):
            return False

        event = self.event
        event_iface = next(event.__implemented__.interfaces())

        rule = self.rule
        if rule and event_iface != rule.rule.event:
            return False

        return True

    def get_history_comment(self):
        """ Given an object and a IActionSucceededEvent,
        extract the comment of the transition.
        """
        action = self.event.action
        if not action:
            return ""
        history = self.event.object.workflow_history
        for transition in reversed(history[self.event.workflow.id]):
            if transition.get("action") == action:
                return transition.get("comments", "")
        return ""

    @property
    @memoize
    def trackWorkingCopies(self):
        registry = getUtility(IRegistry)
        return registry[
            "collective.auditlog.interfaces.IAuditLogSettings.trackworkingcopies"
        ]  # noqa

    def _getObjectInfo(self, obj):
        return getObjectInfo(obj)

    @memoize
    def getLogEntry(self):
        """ Get's a log entry for your action
        """
        event = self.event
        obj = event.object
        data = {"info": ""}
        environ = getattr(self.request, "environ", {})

        # the order of those interface checks matters since some interfaces
        # inherit from others
        if IObjectRemovedEvent.providedBy(event):
            # need to keep track of removed events so it doesn't get called
            # more than once for each object
            action = "removed"
        elif IObjectCreatedEvent.providedBy(event) or IObjectAddedEvent.providedBy(
            event
        ):
            action = "added"
        elif IObjectMovedEvent.providedBy(event):
            # moves can also be renames. Check the parent object
            if event.oldParent == event.newParent:
                if self.rule is None or "Rename" in self.rule.rule.title:
                    info = {"previous_id": event.oldName}
                    data["info"] = json.dumps(info)
                    action = "rename"
                else:
                    # cut out here, double action for this event
                    return True
            else:
                if self.rule is None or "Moved" in self.rule.rule.title:
                    parent_path = "/".join(event.oldParent.getPhysicalPath())
                    previous_location = u"{0}/{1}".format(parent_path, event.oldName)
                    info = {"previous_location": previous_location}
                    data["info"] = json.dumps(info)
                    action = "moved"
                else:
                    # step out immediately since this could be a double action
                    return True
        elif IObjectModifiedEvent.providedBy(event):
            action = "modified"
        elif IActionSucceededEvent.providedBy(event):
            info = {"transition": event.action, "comments": self.get_history_comment()}
            data["info"] = json.dumps(info)
            action = "workflow"
        elif IObjectClonedEvent.providedBy(event):
            action = "copied"
        elif ICheckinEvent.providedBy(event):
            info = {"message": event.message}
            data["info"] = json.dumps(info)
            action = "checked in"
            environ["disable.auditlog"] = True
            data["working_copy"] = "/".join(obj.getPhysicalPath())
            obj = event.baseline
        elif IBeforeCheckoutEvent.providedBy(event):
            action = "checked out"
            environ["disable.auditlog"] = True
        elif ICancelCheckoutEvent.providedBy(event):
            action = "cancel check out"
            environ["disable.auditlog"] = True
            data["working_copy"] = "/".join(obj.getPhysicalPath())
            obj = event.baseline
        elif IUserLoggedInEvent.providedBy(event):
            action = "logged in"
            info = {"user": event.object.getUserName()}
            data["info"] = json.dumps(info)
        elif IUserLoggedOutEvent.providedBy(event):
            action = "logged out"
        else:
            logger.warn("no action matched")
            return True

        if IWorkingCopy.providedBy(obj):
            # if working copy, iterate, check if Track Working Copies is
            # enabled
            if not self.trackWorkingCopies:
                # if not enabled, we only care about checked messages
                if "check" not in action:
                    return True
            # if enabled in control panel, use original object and move
            # working copy path to working_copy
            data["working_copy"] = "/".join(obj.getPhysicalPath())
            if WorkingCopyRelation:
                relationships = obj.getReferences(WorkingCopyRelation.relationship)
            else:
                relationships = []
            # check relationships, if none, something is wrong, not logging
            # action
            if len(relationships) <= 0:
                return True
            obj = relationships[0]

        data.update(self._getObjectInfo(obj))
        data["action"] = action
        return data

    def _addLogEntry(self, logentry):
        addLogEntry(self.event.object, logentry)

    def __call__(self):
        if self.can_execute:
            self._addLogEntry(self.getLogEntry())
        return True


class AuditAddForm(AddForm):

    schema = IAuditAction
    label = u"Add Audit Action"
    form_name = u"Configure element"

    def create(self, data):
        a = AuditAction()
        return a


class AuditEditForm(EditForm):

    schema = IAuditAction
    label = u"Edit Audit Action"
    form_name = u"Configure element"
