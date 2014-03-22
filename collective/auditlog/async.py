from zope.component import getUtility
from collective.auditlog.models import LogEntry
from collective.auditlog import db
from collective.auditlog import td

try:
    from plone.app.async.interfaces import IAsyncService
    ASYNC_INSTALLED = True
except ImportError:
    ASYNC_INSTALLED = False

import logging

logger = logging.getLogger('collective.auditlog')


def runJob(context, **data):
    # make sure to join the transaction before we start
    session = db.getSession()
    tdata = td.get()
    if not tdata.registered:
        tdata.register(session)

    log = LogEntry(**data)
    session.add(log)


def queueJob(obj, *args, **kwargs):
    """
    queue a job async if available.
    otherwise, just run normal
    """
    if ASYNC_INSTALLED:
        try:
            async = getUtility(IAsyncService)
            async.queueJob(runJob, obj, *args, **kwargs)
        except:
            logger.exception(
                "Error using plone.app.async with "
                "collective.auditlog. logging without "
                "plone.app.async...")
            runJob(obj, *args, **kwargs)
    else:
        runJob(obj, *args, **kwargs)
