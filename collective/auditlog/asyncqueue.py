# coding=utf-8
from collective.auditlog import db
from collective.auditlog import td
from collective.auditlog.models import LogEntry
from Products.CMFPlone.utils import safe_unicode


try:
    import collective.celery
    from collective.auditlog.tasks import queue_job
    from celery.utils.log import get_task_logger

    logger = get_task_logger(__name__)
except ImportError:
    queue_job = None
    import logging

    logger = logging.getLogger("collective.auditlog")


def runJob(context, **data):
    # make sure to join the transaction before we start
    session = db.getSession()
    tdata = td.get()
    if not tdata.registered:
        tdata.register(session)

    for key in data:
        value = data[key]
        if isinstance(value, str):
            data[key] = safe_unicode(value)

    log = LogEntry(**data)
    session.add(log)


def queueJob(obj, *args, **kwargs):
    """
    queue a job async if available.
    otherwise, just run normal
    """
    if queue_job and kwargs["action"] != "Undo from ZMI":
        queue_job.delay(obj, *args, **kwargs)
    else:
        runJob(obj, *args, **kwargs)
