from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


def getEngine(conn_string=None):
    if conn_string is None:
        registry = getUtility(IRegistry)
        conn_string = registry['collective.auditlog.connectionstring']
    return create_engine(conn_string)


def getSession(conn_string=None, engine=None):
    if engine is None:
        engine = getEngine(conn_string)
    return sessionmaker(bind=engine)
