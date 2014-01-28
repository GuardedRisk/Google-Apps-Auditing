import httplib2
import os
import sys
import time

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

from sqlalchemy.exc import OperationalError

from config import Configuration
from models import *

try:
    import geoip2.database as geoipdb
except ImportError:
    print ("GeoIP is missing, please install dependency")

def main():
    config = Configuration()
    credentials = config.get_credentials()

    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Construct the service object for the interacting with the Admin Reports API.
    service = discovery.build('admin', 'reports_v1', http=http)
    activities = service.activities()

    settings = config.settings
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    try:
        login_list = activities.list(userKey='all', applicationName='login', maxResults=1000).execute()
        DBSession.query(LoginItem).first()

        print("Success!")
    except client.AccessTokenRefreshError:
        print("Failure. Access token is invalid. Please re-run the tool to get a new access token.")
    except OperationalError:
        print("Database has not been initialised. Please run acctwatch_initdb.")
    except:
        print("Some other unknown error occured")

if __name__ == '__main__':
    main()

