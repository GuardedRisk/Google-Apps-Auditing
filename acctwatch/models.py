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
            Column('guid', String, index=True),
            Column('time', DateTime(timezone=True)),
            Column('success', Boolean, default=False, nullable=False),
            Column('failure', String, nullable=True),
            Column('ip', String, nullable=False),
            )

    actor = relationship("Actor", backref="logins", secondary="actor_logins")
    location = relationship("Location", backref="logins", secondary="login_locations")

class ActorLogins(Base):
    __table__ = Table('actor_logins', Base.metadata, 
            Column('lid', Integer, ForeignKey('login_item.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False),
            Column('aid', String, ForeignKey('actor.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False),

            PrimaryKeyConstraint('lid', 'aid'),
            )

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

class LoginLocation(Base):
    __table__ = Table('login_locations', Base.metadata,
            Column('loc_id', Integer, ForeignKey('location.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False),
            Column('login_id', Integer, ForeignKey('login_item.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False),

            PrimaryKeyConstraint('loc_id', 'login_id'),
            )


