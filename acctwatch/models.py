from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    )

DBSession = scoped_session(sessionmaker())
Base = declarative_base()

class LoginItem(Base):
    __table__ = Table('login_item', Base.metadata,
            Column('id', Integer, primary_key=True, unique=True, autoincrement=True),
            Column('aid', String, ForeignKey('actor.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False),
            Column('lid', Integer, ForeignKey('location.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=True),
            Column('guid', String, index=True),
            Column('time', DateTime(timezone=True)),
            Column('success', Boolean, default=False, nullable=False),
            Column('failure', String, nullable=True),
            Column('ip', String, nullable=False),
            )

    actor = relationship("Actor", backref="logins")
    location = relationship("Location", backref="logins")

class Actor(Base):
    __table__ = Table('actor', Base.metadata, 
            Column('id', String, primary_key=True, unique=True),
            Column('email', String),
            )

class Location(Base):
    __table__ = Table('location', Base.metadata, 
            Column('id', Integer, primary_key=True, unique=True),
            Column('location', String(), unique=True, index=True)
            )
