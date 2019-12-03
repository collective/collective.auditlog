from App.Undo import decode64
from App.Undo import UndoSupport
from collective.auditlog.interfaces import AuditableActionPerformedEvent
from zope.event import notify
from zope.i18nmessageid import MessageFactory

import permissions
import transaction


MessageFactory = MessageFactory("collective.auditlog")


def manage_undo_transactions_with_audit(self, transaction_info=(), REQUEST=None):
    """
    """
    tids = []
    descriptions = []
    for tid in transaction_info:
        tid = tid.split()
        if tid:
            tids.append(decode64(tid[0]))
            descriptions.append(tid[-1])

    if tids:
        note = "Undo %s" % " ".join(descriptions)
        transaction.get().note(note)
        self._p_jar.db().undoMultiple(tids)
        obj = getattr(REQUEST, "context", self)
        notify(AuditableActionPerformedEvent(obj, REQUEST, "Undo from ZMI", note))

    if REQUEST is None:
        return
    REQUEST["RESPONSE"].redirect("%s/manage_UndoForm" % REQUEST["URL1"])
    return ""


# monkey patch undo to be able to audit ZMI undo operations
UndoSupport.manage_undo_transactions = manage_undo_transactions_with_audit
