from zope.i18nmessageid import MessageFactory
MessageFactory = MessageFactory('collective.auditlog')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
