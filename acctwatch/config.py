import argparse
import os
import sys
from ConfigParser import (
        SafeConfigParser,
        NoOptionError,
        )

from oauth2client import file
from oauth2client import client
from oauth2client import tools

# Parser for command-line arguments.
parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[tools.argparser]
        )
parser.add_argument('--section', nargs='?', help='The section to read from the configuration file.', default='DEFAULT')
parser.add_argument('config', help='Configuration file.')

def str2bool(truthy):
    return truthy[0].lower() in ('y', 't')

class Configuration(object):
    def __init__(self):
        # Parse the command-line flags.
        flags = parser.parse_args()

        config_defaults = {}
        config_defaults['here'] = os.path.dirname(os.path.abspath(flags.config))
        config = SafeConfigParser(config_defaults)
        config.readfp(open(flags.config))

        if flags.section != 'DEFAULT' and not config.has_section(flags.section):
            parser.error('Specified section doesn\'t exist in configuration.')

        try:
            # CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
            # application, including client_id and client_secret. You can see the Client ID
            # and Client secret on the APIs page in the Cloud Console:
            # <https://cloud.google.com/console>
            self.CLIENT_SECRETS = config.get(flags.section, 'secrets')
            self.CLIENT_CREDENTIALS = config.get(flags.section, 'credentials')
            self.INTERVAL = int(config.get(flags.section, 'interval'))
            self.WITH_GEOIP = str2bool(config.get(flags.section, 'geoip.enabled'))
            self.email = {}
        except NoOptionError as e:
            parser.error('Unable to get required parameter from config: {}'.format(e))

        # Set up a Flow object to be used for authentication.
        # Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
        # NEED. For more information on using scopes please see
        # <https://developers.google.com/+/best-practices>.
        self.FLOW = client.flow_from_clientsecrets(self.CLIENT_SECRETS,
                scope=[
                    'https://www.googleapis.com/auth/admin.reports.audit.readonly',
                    'https://www.googleapis.com/auth/admin.reports.usage.readonly',
                    ],
                message=tools.message_if_missing(self.CLIENT_SECRETS)
                )

        # If the credentials don't exist or are invalid run through the native client
        # flow. The Storage object will ensure that if successful the good
        # credentials will get written back to the file.
        storage = file.Storage(self.CLIENT_CREDENTIALS)
        self.credentials = storage.get()
        if self.credentials is None or self.credentials.invalid:
            self.credentials = tools.run_flow(FLOW, storage, flags) 

    def get_credentials(self):
        return self.credentials
