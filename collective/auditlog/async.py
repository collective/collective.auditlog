from zope.component import getUtility
try:
    from plone.app.async.interfaces import IAsyncService
    # XXX
    # XXX Disable until we do something about skin scripts...
    # XXX
    ASYNC_INSTALLED = False
except ImportError:
    ASYNC_INSTALLED = False

import logging

logger = logging.getLogger('collective.auditlog')


def runJob(context, *args, **kwargs):
    context.save_action(*args, **kwargs)


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
            runJob(*args, **kwargs)
    else:
        runJob(*args, **kwargs)
