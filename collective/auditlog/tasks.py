from celery.utils.log import get_task_logger
from collective.celery import task


logger = get_task_logger(__name__)


@task(name="audit")
def queue_job(obj, *args, **kwargs):
    from collective.auditlog.asyncqueue import runJob

    logger.warn(f"Logging action on {obj.absolute_url_path()}")
    runJob(obj, *args, **kwargs)
