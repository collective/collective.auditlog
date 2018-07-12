from Products.CMFCore.utils import getToolByName
from collective.auditlog import td
from collective.auditlog.async import queueJob
from datetime import datetime
from plone.uuid.interfaces import IUUID
from zope.component.hooks import getSite
from zope.globalrequest import getRequest


def getUID(context):
    uid = IUUID(context, None)
    if uid is not None:
        return uid

    if hasattr(context, 'UID'):
        return context.UID()

    try:
        return '/'.join(context.getPhysicalPath())
    except AttributeError:
        pass

    try:
        return context.id
    except AttributeError:
        return ''


def getHostname(request):
    """
    stolen from the developer manual
    """

    if "HTTP_X_FORWARDED_HOST" in request.environ:
        # Virtual host
        host = request.environ["HTTP_X_FORWARDED_HOST"]
    elif "HTTP_HOST" in request.environ:
        # Direct client request
        host = request.environ["HTTP_HOST"]
    else:
        return None

    # separate to domain name and port sections
    host = host.split(":")[0].lower()

    return host


def getUser(context):
    portal_membership = getToolByName(context, 'portal_membership')
    return portal_membership.getAuthenticatedMember()


def getObjectInfo(obj):
    """ Get basic information about an object for logging.
    This only includes information available on the object itself. Some fields
    are missing because they depend on the event or rule that was triggered.
    """
    data = dict(
        performed_on=datetime.utcnow(),
        user=getUser(obj).getUserName(),
        site_name=getHostname(getRequest()),
        uid=getUID(obj),
        type=obj.portal_type,
        title=obj.Title(),
        path='/'.join(obj.getPhysicalPath())
    )
    return data


def addLogEntry(data):
    tdata = td.get()
    if not tdata.registered:
        tdata.register()

    queueJob(getSite(), **data)
