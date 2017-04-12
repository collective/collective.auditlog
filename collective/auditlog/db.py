# coding=utf-8
from json import loads
from plone.registry.interfaces import IRegistry
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from zope.component import getUtility
from zope.globalrequest import getRequest


def getEngine(conn_string=None, conn_parameters=None, req=None):
    """
    Cache this on the request object
    """
    if req is None:
        req = getRequest()
    if req and 'sa.engine' in req.environ:
        engine = req.environ['sa.engine']
    else:
        if conn_string is None:
            registry = getUtility(IRegistry)
            conn_string = registry['collective.auditlog.interfaces.IAuditLogSettings.connectionstring']  # noqa
        if conn_parameters is None:
            conn_parameters = registry['collective.auditlog.interfaces.IAuditLogSettings.connectionparameters']  # noqa
        if not conn_parameters:
            conn_parameters = {}
        elif isinstance(conn_parameters, basestring):
            conn_parameters = loads(conn_parameters)
        engine = create_engine(conn_string, **conn_parameters)
        if req:
            req.environ['sa.engine'] = engine
    return engine


def getSession(conn_string=None, engine=None, req=None):
    """
    same, cache on request object
    """
    if engine is None:
        engine = getEngine(conn_string)
    if req is None:
        req = getRequest()
    if req and 'sa.session' in req.environ:
        session = req.environ['sa.session']
    else:
        Session = scoped_session(sessionmaker(bind=engine))
        session = Session()
        if req:
            req.environ['sa.session'] = session
    return session
