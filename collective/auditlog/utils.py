from Acquisition import aq_parent
from collective.auditlog import td
from collective.auditlog.asyncqueue import queueJob
from collective.auditlog.catalog import catalogEntry
from collective.auditlog.interfaces import BeforeStoreAuditlogEntryEvent
from datetime import datetime
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import get_installer
from Products.CMFPlone.utils import pretty_title_or_id
from Zope2 import app
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.hooks import getSite as getSiteHook
from zope.event import notify
from zope.globalrequest import getRequest


def is_installed():
    try:
        site = getSite()
        installer = get_installer(site)
        installed = installer.is_product_installed("collective.auditlog")
        registry = queryUtility(IRegistry, context=site)
        installed = (
            installed
            and registry
            and ("collective.auditlog.interfaces.IAuditLogSettings.storage" in registry)
        )
    except AttributeError:
        installed = False
    return installed


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


def getHostname():
    """
    stolen from the developer manual
    """
    request = getRequest()
    environ = getattr(request, "environ", {})
    if "HTTP_X_FORWARDED_HOST" in environ:
        # Virtual host
        host = environ["HTTP_X_FORWARDED_HOST"]
    elif "HTTP_HOST" in environ:
        # Direct client request
        host = environ["HTTP_HOST"]
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
                    if f" /{plone_site}/" in info:
                        site = zope_root[plone_site]
    return site


def getUser():
    username = "unknown"
    try:
        portal_membership = getToolByName(getSite(), "portal_membership")
        user = portal_membership.getAuthenticatedMember()
        username = user.getUserName()
    except AttributeError:
        try:
            username = getRequest().other.get("AUTHENTICATED_USER").getUserName()
        except AttributeError:
            pass
    return username


def getObjectInfo(obj):
    """Get basic information about an object for logging.
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
        user=getUser(),
        site_name=getHostname(),
        uid=getUID(obj),
        type=getattr(obj, "portal_type", ""),
        title=pretty_title_or_id(aq_parent(obj), obj),
        path="/".join(obj.getPhysicalPath())
        if getattr(obj, "getPhysicalPath", False)
        else "/",
    )
    return data


def addLogEntry(obj, data):
    # XXX getLogEntry sometime returns True, probably it should just return None
    if not data or data is True:
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
