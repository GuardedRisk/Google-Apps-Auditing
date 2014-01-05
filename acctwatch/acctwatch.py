import httplib2
import os
import sys

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

        for login_item in login_list['items']:
            print login_item['actor']['email']
            print '\t' + login_item['ipAddress']
            print '\t' + login_item['id']['time']

            login_event = login_item['events']
            for event in login_event:
                print '\t' + event['type'] + ': ' + event['name']
                if 'parameters' not in event:
                    continue
                for param in event['parameters']:
                    print '\t\t' + param['name'] + ': ' + param['value']

    except client.AccessTokenRefreshError:
      print ("The credentials have been revoked or expired, please re-run"
        "the application to re-authorize")


# For more information on the Admin Reports API you can visit:
#
#   https://developers.google.com/admin-sdk/reports/
#
# For more information on the Admin Reports API Python library surface you
# can visit:
#
#   https://developers.google.com/resources/api-libraries/documentation/admin/reports_v1/python/latest/
#
# For information on the Python Client Library visit:
#
#   https://developers.google.com/api-client-library/python/start/get_started
if __name__ == '__main__':
    main()
