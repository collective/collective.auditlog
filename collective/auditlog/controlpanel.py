from Products.Five.browser import BrowserView

from zope.component import queryUtility
from plone.registry.interfaces import IRegistry

from plone.app.registry.browser import controlpanel

from collective.auditlog.interfaces import IAuditLogSettings, _


class AuditLogSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IAuditLogSettings
    label = _(u"Audit Log settings")
    description = _(u"""""")

    def updateFields(self):
        super(AuditLogSettingsEditForm, self).updateFields()


    def updateWidgets(self):
        super(AuditLogSettingsEditForm, self).updateWidgets()

class AuditLogSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = AuditLogSettingsEditForm

