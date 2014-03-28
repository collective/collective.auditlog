from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from zope.globalrequest import getRequest
from collective.auditlog.interfaces import IAuditLogSettings


def getEngine(conn_string=None, req=None):
    """
    cache this on the request object
    """
    if req is None:
        req = getRequest()
    if req and 'sa.engine' in req.environ:
        engine = req.environ['sa.engine']
    else:
        if conn_string is None:
            registry = getUtility(IRegistry)
#	    settings = registry.forInterface(IAuditLogSettings)
#            conn_string = registry['collective.auditlog.connectionstring']
#	    conn_string = self.settings.connectionstring
	    conn_string = registry['collective.auditlog.interfaces.IAuditLogSettings.connectionstring']
        engine = create_engine(conn_string)
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
