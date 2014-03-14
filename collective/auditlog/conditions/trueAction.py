from OFS.SimpleItem import SimpleItem

from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema

from zope.component.interfaces import IObjectEvent

from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData

from plone.app.contentrules.browser.formhelper import AddForm, EditForm

from collective.auditlog import MessageFactory as _

from plone.app.linkintegrity.interfaces import ILinkIntegrityInfo


class ITrueActionCondition(Interface):
    """Interface for the configurable aspects of the True Action condition.
    This is also used to create add and edit forms, below..."""

    action = schema.TextLine(
        title=_(u"True Action"),
        description=_(u"""The action to be tested as true. Type one of the
                          keywords into the text box to test that action.
                          The available actions are ${delete}, ${move},
                          and ${rename}."""),
        required=True)


class TrueActionCondition(SimpleItem):
    """The actual persistent implementation of the true action condition
       element"""
    implements(ITrueActionCondition, IRuleElementData)

    action = u''
    element = "collective.auditlogcondition.TrueAction"

    @property
    def summary(self):
        return _(u"True action is ${act}", mapping=dict(act=self.action))


class TrueActionConditionExecutor(object):
    """The executor for this condition
    This is registered as an adapter in configure.zcml"""

    implements(IExecutable)
    adapts(Interface, ITrueActionCondition, IObjectEvent)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        request = getattr(self.event.object, 'REQUEST', None)
        event = self.event
        obj = self.event.object
        action = self.element.action
        trueAction = False

        if "delete" in action:
            try:
                if request is None:
                    trueAction = True
                else:
                    info = ILinkIntegrityInfo(request)
                    if info.isConfirmedItem(obj):
                        trueAction = True
            except:
                trueAction = False

        if "move" in action:
            try:
                oldParent = event.oldParent
                newParent = event.newParent
                oldName = event.oldName
                newName = event.newName
                if oldParent and newParent and oldParent != newParent and \
                        oldName == newName:
                    trueAction = True
            except:
                trueAction = False

        if "rename" in action:
            try:
                oldParent = event.oldParent
                newParent = event.newParent
                oldName = event.oldName
                newName = event.newName
                if oldParent == newParent and oldName != newName:
                    trueAction = True
            except:
                trueAction = False

        return trueAction


class TrueActionAddForm(AddForm):
    """An add form for portal type conditions"""
    form_fields = form.FormFields(ITrueActionCondition)
    label = ("Add True Action Condition")
    description = ("""A True Action condition makes the rule apply only to
                      content when the specified action truly happens (ie
                      ${delete} is only True after the content has been
                      Confirmed for Link Integrity.)""")
    form_name = ("Configure element")

    def create(self, data):
        c = TrueActionCondition()
        form.applyChanges(c, self.form_fields, data)
        return c


class TrueActionEditForm(EditForm):
    """An edit form"""

    form_fields = form.FormFields(ITrueActionCondition)
    label = ("Edit True Action Condition")
    description = ("""A True Action condition makes the rule apply only to
                      content when the specified action truly happens (ie
                      ${delete} is only True after the content has been
                      Confirmed for Link Integrity.)""")
    form_name = ("Configure element")
