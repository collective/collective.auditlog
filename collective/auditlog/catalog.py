from AccessControl import ClassSecurityInfo
from collective.auditlog import db
from collective.auditlog.models import LogEntry
from datetime import datetime
from Globals import InitializeClass
from plone.api import portal as portal_api
from Products.CMFCore.interfaces._content import ICatalogAware
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.ZCTextIndex.HTMLSplitter import HTMLWordSplitter
from Products.ZCTextIndex.Lexicon import CaseNormalizer
from Products.ZCTextIndex.Lexicon import StopWordRemover
from Products.ZCTextIndex.ZCTextIndex import PLexicon
from zope.interface import implements
from zope.interface import Interface


class Empty(object):
    """
    """


class IAuditCatalog(Interface):
    """
    """


class AuditCatalog(CatalogTool):
    """
    A specific launch catalog tool
    """

    implements(IAuditCatalog)

    title = "specific catalog"
    id = "audit_catalog"
    portal_type = meta_type = "AuditCatalog"
    plone_tool = 1

    security = ClassSecurityInfo()
    _properties = ({"id": "title", "type": "string", "mode": "w"},)

    def __init__(self):
        ZCatalog.__init__(self, self.id)
        self.updateIndexes()

    def updateIndexes(self):
        if not getattr(self, "audit_lexicon", None):
            # installing, add lexicon, indexes and metadata
            self.addIndex("last_audited_date", "DateIndex")
            self.addIndex("audited_action", "KeywordIndex")
            self.addColumn("Title")
            self.addColumn("id")
            self.addColumn("UID")
            self.addColumn("last_audited_date")
            self.addColumn("audited_action")
            l = PLexicon(
                "audit_lexicon",
                "",
                HTMLWordSplitter(),
                CaseNormalizer(),
                StopWordRemover(),
            )
            self._setObject("audit_lexicon", l)
        catalog = portal_api.get_tool("portal_catalog")
        indexes = catalog._catalog.indexes
        for name, index in indexes.items():
            if name in self._catalog.indexes.keys():
                continue
            if index.meta_type == "DateRecurringIndex":
                continue
            elif index.meta_type == "ZCTextIndex":
                extras = Empty()
                extras.doc_attr = name
                extras.index_type = "Okapi BM25 Rank"
                extras.lexicon_id = "audit_lexicon"
                self.addIndex(name, index.meta_type, extras)
            else:
                self.addIndex(name, index.meta_type)


InitializeClass(AuditCatalog)


def catalogEntry(obj, data):
    if not ICatalogAware.providedBy(obj):
        return
    catalog = portal_api.get_tool("audit_catalog")
    catalog.updateIndexes()
    action = getattr(obj, "audited_action", None)
    if action is None:
        action = [data["action"]]
    else:
        if data["action"] not in action:
            action.append(data["action"])
    obj.audited_action = action
    obj.last_audited_date = datetime.now()
    catalog.catalog_object(obj)


def searchAudited(from_date=None, to_date=None, actions=None, **query):
    session = db.getSession()
    lines = session.query(LogEntry)
    if from_date is not None:
        lines = lines.filter(LogEntry.performed_on > from_date)
    if to_date is not None:
        lines = lines.filter(LogEntry.performed_on < to_date)
    if actions is not None:
        lines = lines.filter(LogEntry.action.in_(actions))
    uids = [line.uid for line in lines]
    uids = list(set(uids))
    catalog = portal_api.get_tool("audit_catalog")
    return catalog.unrestrictedSearchResults(UID=uids, **query)
