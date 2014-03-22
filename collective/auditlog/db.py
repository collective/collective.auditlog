from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from zope.globalrequest import getRequest


def getEngine(conn_string=None, req=None):
    if req is None:
        req = getRequest()
    if 'sa.engine' in req.environ:
        engine = req.environ['sa.engine']
    else:
        if conn_string is None:
            registry = getUtility(IRegistry)
            conn_string = registry['collective.auditlog.connectionstring']
        engine = create_engine(conn_string)
    req.environ['sa.engine'] = engine
    return engine


def getSession(conn_string=None, engine=None, req=None):
    if engine is None:
        engine = getEngine(conn_string)
    if req is None:
        req = getRequest()
    if 'sa.session' in req.environ:
        session = req.environ['sa.session']
    else:
        Session = scoped_session(sessionmaker(bind=engine))
        session = Session()
    req.environ['sa.session'] = session
    return session
