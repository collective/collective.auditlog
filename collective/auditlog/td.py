"""
Why all this you ask? Well, we need to pay attention to the plone transactions
and sqlite does not play well with transaction management.
So we get to do something funky with aborting transactions and joining in
on the zope transaction
"""

from collective.auditlog import db
from collective.auditlog.models import Base
from logging import getLogger
from plone.app.contentrules import handlers as cr_handlers
from transaction.interfaces import IDataManagerSavepoint
from transaction.interfaces import ISavepointDataManager
from zope.interface import implementer

import threading
import traceback
import transaction as transaction_manager


logger = getLogger(__name__)

tranaction_data = threading.local()


def get():
    try:
        return tranaction_data.data
    except AttributeError:
        tranaction_data.data = TransactionData()
        return tranaction_data.data


@implementer(ISavepointDataManager)
class DataManager(object):
    def __init__(self, td):
        self._session = None
        self.td = td
        self.savepoints = []

    @property
    def session(self):
        if self._session is None:
            self._session = db.getSession()
            engine = db.getEngine()
            if not engine.dialect.has_table(engine, "audit"):
                Base.metadata.create_all(bind=engine)
        return self._session

    def commit(self, trans):
        if self.td.registered:
            try:
                self.session.commit()
            except:
                logger.error(
                    "Error during audit log commit. "
                    "Error stack: %s" % (traceback.format_exc())
                )
        self.td.reset()
        self._clear_session()

    def tpc_begin(self, trans):
        pass

    def tpc_vote(self, trans):
        pass

    def tpc_finish(self, trans):
        self.td.reset()
        self._clear_session()

    def tpc_abort(self, trans):
        pass

    def abort(self, trans):
        if self.td.registered:
            self.session.expunge_all()
            # so content rules can match again
            cr_handlers.close(None)
        self.td.reset()
        self._clear_session()

    @property
    def savepoint(self):
        return self._savepoint

    def _savepoint(self):
        sp = Savepoint(self)
        self.savepoints.append(sp)
        return sp

    def should_retry(self, error):
        pass

    def sortKey(self):
        # Sort normally
        return "collective.auditlog"

    def _clear_session(self):
        if self._session is not None:
            db.session_factory.remove()
            self._session = None


@implementer(IDataManagerSavepoint)
class Savepoint:
    def __init__(self, dm):
        self.dm = dm
        self.old = dm.session.new.copy()

    def rollback(self):
        if self.dm.td.registered:
            self.dm.session.expunge_all()
            if len(self.old) > 0:
                for ob in self.old:
                    self.dm.session.add(ob)
            else:
                # allow content rules to run again
                cr_handlers.close(None)


class TransactionData(object):
    def __init__(self):
        self.joined = False
        self.registered = False
        self.items = []
        self.dm = None

    def join(self):
        transaction = transaction_manager.get()
        found = False
        for resource in transaction._resources:
            if isinstance(resource, DataManager):
                found = True
                self.dm = resource
                break
        if not found:
            self.dm = DataManager(self)
            transaction.join(self.dm)
        self.joined = True

    def register(self, session=None):
        self.registered = True
        if not self.joined:
            self.join()
        if session and self.dm:
            self.dm._session = session

    def reset(self):
        self.items = []
        self.registered = False
        self.joined = False
