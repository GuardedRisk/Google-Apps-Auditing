import httplib2
import os
import sys
import traceback

import time
import datetime

import apiclient
from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

from sqlalchemy import engine_from_config
from sqlalchemy.exc import IntegrityError

from config import Configuration
from models import *

try:
    import geoip2.database as geoipdb
    from geoip2.errors import AddressNotFoundError
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

    geoip_reader = geoipdb.Reader(settings['geoip_db'])

    print ("Started watching for new logins")

    while 1:
        try:
            all_new = True

            request = activities.list(userKey='all', applicationName='login', maxResults=1000)
            response = None

            while all_new:
                response = request.execute()

                for login_item in response['items']:
                    login_id = login_item['id']

                    exists = DBSession.query(LoginItem).filter(LoginItem.guid == login_id['uniqueQualifier']).first()

                    if exists:
                        all_new = False
                        continue



                    litem = LoginItem(guid=login_id['uniqueQualifier'], time=datetime.datetime.strptime(login_id['time'], '%Y-%m-%dT%H:%M:%S.%fZ'), ip=login_item['ipAddress'])
                    lactor = DBSession.query(Actor).filter(Actor.id == login_item['actor']['profileId']).first()

                    if lactor:
                        litem.actor.append(lactor)
                    else:
                        litem.actor.append(Actor(id=login_item['actor']['profileId'], email=login_item['actor']['email']))


                    try:
                        geoip = geoip_reader.city(login_item['ipAddress'])
                        geoip_results = '{}, {}, {}'.format(geoip.city.name, geoip.subdivisions.most_specific.name, geoip.country.name)

                        llocation = DBSession.query(Location).filter(Location.location == geoip_results).first()

                        if llocation:
                            litem.location.append(llocation)
                        else:
                            litem.location.append(Location(location=geoip_results))

                        print ("New login found for \"{}\" at \"{}\", from \"{}\" ({})".format(login_item['actor']['email'], login_id['time'], geoip_results, login_item['ipAddress']))
                    except AddressNotFoundError:
                        print ("New login found for \"{}\" at \"{}\", from \"unknown\" ({})".format(login_item['actor']['email'], login_id['time'], login_item['ipAddress']))

                    login_event = login_item['events']
                    for event in login_event:
                        if event['type'] == 'login':
                            if event['name'] == 'login_success':
                                litem.success = True
                            if event['name'] == 'login_failure':
                                litem.success = False
                                failed_params = event['parameters']

                                litem.failure = ''
                                for fail_param in failed_params:
                                    if fail_param['name'] == 'login_type':
                                        litem.failure = '{}{}'.format(fail_param['value'], litem.failure)
                                    if fail_param['name'] == 'login_failure_type':
                                        litem.failure = '{} - {}'.format(litem.failure, fail_param['value'])

                    DBSession.add(litem)
                    DBSession.commit()

                if all_new == True:
                    old_request = request
                    request = activities.list_next(old_request, response)

                    if request is None:
                        all_new = False
                        break

        except client.AccessTokenRefreshError:
            print ("The credentials have been revoked or expired, please re-run"
                    "the application to re-authorize")
        except apiclient.errors.HttpError as e:
            print ("Google returned us an error. {}".format(e))
        except KeyboardInterrupt:
            print ("Received the signal to quit")
            exit(0)
        except:
            print ("Some other error occured...")
            traceback.print_exc()

        time.sleep(config.INTERVAL)



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
