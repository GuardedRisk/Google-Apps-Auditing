import argparse
import httplib2
import os
import sys

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

# Parser for command-line arguments.
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])


# CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret. You can see the Client ID
# and Client secret on the APIs page in the Cloud Console:
# <https://cloud.google.com/console>
CLIENT_SECRETS = os.path.join(os.getcwd(), 'client_secrets.json')

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
# NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
  scope=[
      'https://www.googleapis.com/auth/admin.reports.audit.readonly',
      'https://www.googleapis.com/auth/admin.reports.usage.readonly',
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))


def main(argv=None):

  if argv == None:
      argv = sys.argv
  # Parse the command-line flags.
  flags = parser.parse_args(argv[1:])

  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to the file.
  storage = file.Storage('secret_credentials.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(FLOW, storage, flags)

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
        login_event = login_item['events']
        print '\t' + login_item['ipAddress']
        print '\t' + login_item['id']['time']

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
  main(sys.argv)
