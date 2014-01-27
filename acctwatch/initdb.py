import os
import sys
import datetime

from sqlalchemy import engine_from_config
from sqlalchemy.exc import IntegrityError

from models import *

from config import Configuration

def main():
    config = Configuration()
    settings = config.settings
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
