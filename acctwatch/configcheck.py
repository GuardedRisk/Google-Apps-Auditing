import httplib2
import os
import sys
import time

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

from config import Configuration

try:
    import geoip2.database as geoipdb
except ImportError:
    geoipdb = None

def main():
    config = Configuration()
    if config.WITH_GEOIP and not geoipdb:
        print ("GeoIP is enabled, but unable to import module, please check installation. Disabling.")
        config.WITH_GEOIP = False

    credentials = config.get_credentials()

    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Construct the service object for the interacting with the Admin Reports API.
    service = discovery.build('admin', 'reports_v1', http=http)
    activities = service.activities()

    try:
        login_list = activities.list(userKey='all', applicationName='login', maxResults=1000).execute()
        print("Success!")
    except client.AccessTokenRefreshError:
        print("Failure. Access token is invalid.")

if __name__ == '__main__':
    main()

