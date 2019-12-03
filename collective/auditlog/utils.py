# coding=utf-8
from collective.auditlog import td
from collective.auditlog.async import queueJob
from collective.auditlog.catalog import catalogEntry
from collective.auditlog.interfaces import BeforeStoreAuditlogEntryEvent
from datetime import datetime
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Zope2 import app
from zope.component import getUtility
from zope.component.hooks import getSite as getSiteHook
from zope.event import notify
from zope.globalrequest import getRequest


def getUID(context):
    uid = IUUID(context, None)
    if uid is not None:
        return uid

    if hasattr(context, "UID"):
        return context.UID()

    try:
        return "/".join(context.getPhysicalPath())
    except AttributeError:
        pass

    try:
        return context.id
    except AttributeError:
        return "unknown"


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


def getSite():
    site = getSiteHook()
    if site is None:
        # user might be at zope root level. Try to guess site
        zope_root = app()
        plone_sites = zope_root.objectIds("Plone Site")
        if len(plone_sites) == 1:
            # just one plone site, safe bet
            site = zope_root[plone_sites[0]]
        elif len(plone_sites) > 1:
            # many sites. Might be an undo attempt
            request = getRequest()
            if request and "transaction_info" in request.other:
                info = " ".join(request.other["transaction_info"])
                for plone_site in plone_sites:
                    if " /{}/".format(plone_site) in info:
                        site = zope_root[plone_site]
    return site


def getUser(request):
    username = "unknown"
    try:
        portal_membership = getToolByName(getSite(), "portal_membership")
        user = portal_membership.getAuthenticatedMember()
        username = user.getUserName()
    except AttributeError:
        try:
            username = request.other.get("AUTHENTICATED_USER").getUserName()
        except AttributeError:
            pass
    return username


def getObjectInfo(obj, request):
    """ Get basic information about an object for logging.
    This only includes information available on the object itself. Some fields
    are missing because they depend on the event or rule that was triggered.
    """
    obj_id = obj.id
    if callable(obj_id):
        obj_id = obj_id()
    if not obj_id:
        obj_id = "Zope"
    data = dict(
        performed_on=datetime.utcnow(),
        user=getUser(request),
        site_name=getHostname(request),
        uid=getUID(obj),
        type=getattr(obj, "portal_type", ""),
        title=obj.Title() if getattr(obj, "Title", False) else obj_id,
        path="/".join(obj.getPhysicalPath())
        if getattr(obj, "getPhysicalPath", False)
        else "/",
    )
    return data


def addLogEntry(obj, data):
    if not data:
        return
    tdata = td.get()
    if not tdata.registered:
        tdata.register()

    notify(BeforeStoreAuditlogEntryEvent(obj, data))
    queueJob(getSite(), **data)

    registry = getUtility(IRegistry)
    storage = registry[
        "collective.auditlog.interfaces.IAuditLogSettings.storage"
    ]  # noqa
    if storage != "sql":
        catalogEntry(obj, data)
