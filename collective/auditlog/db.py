# coding=utf-8
from App.config import getConfiguration
from json import loads
from plone.registry.interfaces import IRegistry
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from zope.component import getUtility
from zope.globalrequest import getRequest


zope_conf = getConfiguration()
product_conf = getattr(zope_conf, "product_config", {})
config = product_conf.get("collective.auditlog", {})

engine = None
session_factory = None


def getEngine(conn_string=None, conn_parameters=None, req=None):
    """
    Cache this on the request object
    """
    global engine
    if engine is None:
        registry = getUtility(IRegistry)
        if conn_string is None:
            conn_string = config.get("audit-connection-string", None)
        if conn_string is None:
            conn_string = registry[
                "collective.auditlog.interfaces.IAuditLogSettings.connectionstring"
            ]  # noqa
        if conn_parameters is None:
            conn_parameters = config.get("audit-connection-params", None)
        if conn_parameters is None:
            conn_parameters = registry[
                "collective.auditlog.interfaces.IAuditLogSettings.connectionparameters"
            ]  # noqa
        if not conn_parameters:
            conn_parameters = {}
        elif isinstance(conn_parameters, basestring):
            conn_parameters = loads(conn_parameters)
        engine = create_engine(conn_string, **conn_parameters)
    return engine


def getSession(conn_string=None, req=None):
    """
    same, cache on request object
    """
    global engine, session_factory
    if engine is None:
        engine = getEngine(conn_string)
    if session_factory is None:
        session_factory = scoped_session(sessionmaker(bind=engine))
    session = session_factory()
    return session
