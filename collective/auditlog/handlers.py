"""
Handle plone.app.iterate events triggering content rules.
"""


def __init__():

    global checkin_action, checkout_action, cancel_checkout_action
    global moved, added, confirmed_removed, created, execute_rules

    # execute_rules(event) runs rules defined for the parent.
    # See also execute(context, event) to run rules defined for the
    # context (is execute() preferable?)
    # Both functions bubble up the acquisition chain
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

    def checkin_action(event):
        """Handle plone.app.iterate.interfaces.IAfterCheckinEvent"""
        execute_rules(event)

    def checkout_action(event):
        """Handle plone.app.iterate.interfaces.ICheckoutEvent"""
        execute_rules(event)

    def cancel_checkout_action(event):
        """Handle plone.app.iterate.interfaces.ICancelCheckoutEvent"""
        execute_rules(event)

    def added(event):
        """Handle zope.app.container.interfaces.IObjectAddedEvent"""
        execute_rules(event)

    def confirmed_removed(obj, event):
        """Handle Products.Archetypes.interfaces.IBaseObject
           zope.lifecycleevent.interfaces.IObjectRemovedEvent"""
        execute_rules(event)

    def created(event):
        """Handle zope.lifecycleevent.interfaces.IObjectCreatedEvent"""
        execute_rules(event)

    def moved(event):
        """Handle zope.lifecycleevent.interfaces.IObjectMovedEvent"""
        execute_rules(event)

__init__()
