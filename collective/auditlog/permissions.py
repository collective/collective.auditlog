# -*- coding: utf-8 -*-
from AccessControl.SecurityInfo import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles


security = ModuleSecurityInfo("collective.auditlog")

security.declarePublic("ViewAuditlog")
ViewAuditlog = "collective.auditlog: View Auditlog"
setDefaultRoles(ViewAuditlog, ("Manager",))
