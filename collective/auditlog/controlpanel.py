# coding=utf-8
from collective.auditlog.interfaces import IAuditLogSettings, _
from plone.app.registry.browser import controlpanel


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
