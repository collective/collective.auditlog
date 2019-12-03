# coding=utf-8
from collective.auditlog.db import config
from collective.auditlog.interfaces import _
from collective.auditlog.interfaces import IAuditLogSettings
from plone.app.registry.browser import controlpanel


class AuditLogSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IAuditLogSettings
    label = _(u"Audit Log settings")
    description = _(u"""""")

    def updateFields(self):
        super(AuditLogSettingsEditForm, self).updateFields()
        conn_string = config.get("audit-connection-string", None)
        conn_string_field = self.fields.get("connectionstring", None)
        if conn_string is not None and conn_string_field is not None:
            desc = u"""Read-only. The connection string was defined in
                the configuration file.
            """
            conn_string_field.field.required = False
            conn_string_field.field.description = desc
        conn_params = config.get("audit-connection-params", None)
        conn_params_field = self.fields.get("connectionparameters", None)
        if conn_params is not None and conn_params_field is not None:
            desc = u"""Read-only. The connection parameters were
                defined in the configuration file.
            """
            conn_params_field.field.required = False
            conn_params_field.field.description = desc

    def updateWidgets(self):
        super(AuditLogSettingsEditForm, self).updateWidgets()
        conn_string = config.get("audit-connection-string", None)
        conn_string_widget = self.widgets.get("connectionstring", None)
        if conn_string is not None and conn_string_widget is not None:
            conn_string_widget.value = conn_string
            conn_string_widget.mode = "display"
        conn_params = config.get("audit-connection-params", None)
        conn_params_widget = self.widgets.get("connectionparameters", None)
        if conn_params is not None and conn_params_widget is not None:
            conn_params_widget.value = conn_params
            conn_params_widget.mode = "display"


class AuditLogSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = AuditLogSettingsEditForm
