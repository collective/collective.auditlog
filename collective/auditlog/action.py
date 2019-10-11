# coding=utf-8
from Acquisition import aq_base
from Acquisition import aq_parent
from collective.auditlog.async import queueJob
from collective.auditlog.utils import addLogEntry
from collective.auditlog.utils import getObjectInfo
from collective.auditlog.utils import getUID
from datetime import datetime
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
from Products.CMFCore.utils import getToolByName
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
import warnings


class IMissingInterface(Interface):
    pass


try:
    from Products.Archetypes.interfaces import IBaseObject
except ImportError:
    IBaseObject = IMissingInterface

try:
    from Products.Archetypes.interfaces import IObjectEditedEvent
except ImportError:
    IObjectEditedEvent = IMissingInterface

try:
    from Products.Archetypes.interfaces import IObjectInitializedEvent
except ImportError:
    IObjectInitializedEvent = IMissingInterface

try:
    from Products.PloneFormGen.interfaces import IPloneFormGenField
except ImportError:

    class IPloneFormGenField(Interface):
        pass


try:
    from plone.app.iterate.relation import WorkingCopyRelation
except ImportError:
    # Import will fail if we do not have Products.Archetypes
    WorkingCopyRelation = None

try:
    # Plone4 only (formlib)
    from zope.formlib import form

    HAS_FORMLIB = True
except ImportError:
    form = None
    HAS_FORMLIB = False  # Plone 5 will use z3c.form


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
    @memoize
    def request(self):
        """ Try to get a request
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

    def canExecute(self, rule=None, req=None):
        if rule is not None or req is not None:
            msg = (
                "In the next releases the rule and req parameters "
                "will not be supported anymore. "
                "In case you want to customize this product "
                "use the request and rule properties"
            )
            warnings.warn(msg, DeprecationWarning)

        if req is None:
            req = self.request

        if req.environ.get("disable.auditlog", False):
            return False

        event = self.event
        obj = event.object
        event_iface = next(event.__implemented__.interfaces())

        # for archetypes we need to make sure we're getting the right moved
        # event here so we do not duplicate
        if not IObjectEditedEvent.providedBy(event):
            if rule is None:
                rule = self.rule
            if rule and event_iface != rule.rule.event:
                return False
        # if archetypes, initialization also does move events
        if (
            IObjectMovedEvent.providedBy(event)
            and IBaseObject.providedBy(obj)
            and obj.checkCreationFlag()
        ):
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
        return getObjectInfo(obj, self.request)

    @memoize
    def getLogEntry(self):
        """ Get's a log entry for your action
        """
        event = self.event
        obj = event.object
        data = {"info": ""}

        # order of those checks is important since some interfaces
        # base off the others
        if IPloneFormGenField.providedBy(obj):
            # if ploneformgen field, use parent object for modified data
            data["field"] = obj.getId()
            obj = aq_parent(obj)

        # the order of those interface checks matters since some interfaces
        # inherit from others
        if IObjectRemovedEvent.providedBy(event):
            # need to keep track of removed events so it doesn't get called
            # more than once for each object
            action = "removed"
        elif (
            IObjectInitializedEvent.providedBy(event)
            or IObjectCreatedEvent.providedBy(event)
            or IObjectAddedEvent.providedBy(event)
        ):
            action = "added"
        elif IObjectMovedEvent.providedBy(event):
            # moves can also be renames. Check the parent object
            if event.oldParent == event.newParent:
                if rule is None or "Rename" in self.rule.rule.title:
                    info = {"previous_id": event.oldName}
                    data["info"] = json.dumps(info)
                    action = "rename"
                else:
                    # cut out here, double action for this event
                    return True
            else:
                if rule is None or "Moved" in self.rule.rule.title:
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
            self.request.environ["disable.auditlog"] = True
            data["working_copy"] = "/".join(obj.getPhysicalPath())
            obj = event.baseline
        elif IBeforeCheckoutEvent.providedBy(event):
            action = "checked out"
            self.request.environ["disable.auditlog"] = True
        elif ICancelCheckoutEvent.providedBy(event):
            action = "cancel check out"
            self.request.environ["disable.auditlog"] = True
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
        try:  # Remove in 1.4
            can_execute = self.canExecute()
        except TypeError:
            # This grants the compatibility with previous versions of the code
            # in which the two parameters were required
            can_execute = self.canExecute(self.rule, self.request)

        if can_execute:
            self._addLogEntry(self.getLogEntry())
        return True


class AuditAddForm(AddForm):

    # Plone4 only
    form_fields = form.FormFields(IAuditAction) if HAS_FORMLIB else []
    schema = IAuditAction  # needed for Plone5 (z3c.form)
    label = u"Add Audit Action"
    form_name = u"Configure element"

    def create(self, data):
        a = AuditAction()
        HAS_FORMLIB and form.applyChanges(a, self.form_fields, data)
        return a


class AuditEditForm(EditForm):

    # Plone4 only
    form_fields = form.FormFields(IAuditAction) if HAS_FORMLIB else []
    schema = IAuditAction  # needed for Plone5 (z3c.form)

    label = u"Edit Audit Action"
    form_name = u"Configure element"
