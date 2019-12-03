from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Unicode
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class LogEntry(Base):
    __tablename__ = "audit"

    id = Column(Integer, primary_key=True)
    user = Column(Unicode(255), nullable=True)
    performed_on = Column(DateTime, nullable=True)
    uid = Column(String(255))
    type = Column(String(255), nullable=True)
    title = Column(Unicode(255), nullable=True)
    path = Column(String(4096), nullable=True)
    site_name = Column(Unicode(255), nullable=True)
    action = Column(String(255), nullable=True)
    field = Column(Unicode(255), nullable=True)
    working_copy = Column(Unicode(4096), nullable=True)
    info = Column(Unicode(4096), nullable=True)
