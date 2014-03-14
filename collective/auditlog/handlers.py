from zope.component.hooks import getSite
try:
    from plone.app.contentrules.handlers import execute_rules
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


def _execute(event):
    site = getSite()
    try:
        qi = site.portal_quickinstaller
    except AttributeError:
        return
    if qi.isProductInstalled('collective.auditlog'):
        execute_rules(event)


def checkin_action(event):
    """Handle plone.app.iterate.interfaces.IAfterCheckinEvent"""
    _execute(event)


def checkout_action(event):
    """Handle plone.app.iterate.interfaces.ICheckoutEvent"""
    _execute(event)


def cancel_checkout_action(event):
    """Handle plone.app.iterate.interfaces.ICancelCheckoutEvent"""
    _execute(event)


def added(event):
    """Handle zope.app.container.interfaces.IObjectAddedEvent"""
    _execute(event)


def confirmed_removed(obj, event):
    """Handle Products.Archetypes.interfaces.IBaseObject
        zope.lifecycleevent.interfaces.IObjectRemovedEvent"""
    _execute(event)


def created(event):
    """Handle zope.lifecycleevent.interfaces.IObjectCreatedEvent"""
    _execute(event)


def moved(event):
    """Handle zope.lifecycleevent.interfaces.IObjectMovedEvent"""
    _execute(event)
