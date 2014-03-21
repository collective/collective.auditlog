from sqlalchemy import Column, Integer, Unicode, DateTime, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class LogEntry(Base):
    __tablename__ = 'audit'

    id = Column(Integer, primary_key=True)
    user = Column(Unicode, nullable=True)
    performed_on = Column(DateTime, nullable=True)
    uid = Column(String)
    type = Column(String, nullable=True)
    title = Column(Unicode, nullable=True)
    path = Column(String, nullable=True)
    site_name = Column(Unicode, nullable=True)
    action = Column(String, nullable=True)
    field = Column(Unicode, nullable=True)
    working_copy = Column(Unicode, nullable=True)
