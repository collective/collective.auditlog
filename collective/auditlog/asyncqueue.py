from collective.auditlog import db
from collective.auditlog import td
from collective.auditlog.models import LogEntry


try:
    from plone.base.utils import safe_text
except ImportError:
    # BBB Plone 5.2
    from Products.CMFPlone.utils import safe_text

try:
    from celery.utils.log import get_task_logger
    from collective.auditlog.tasks import queue_job

    import collective.celery  # noqa: F401

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
            data[key] = safe_text(value)

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
