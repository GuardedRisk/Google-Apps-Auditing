import os
import sys
import traceback
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
from collections import defaultdict

import time
import datetime
import argparse

from sqlalchemy import engine_from_config
from sqlalchemy.exc import IntegrityError

from config import Configuration
from config import parser as parent_parser
from config import aslist, asbool
from models import *

# Parser for command-line arguments.
parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[parent_parser],
        add_help=False,
        )
parser.add_argument('--email-type', choices=['daily', 'weekly', 'monthly', 'invalid'], help='The email type to create')

def main():
    config = Configuration(extra_parser=parser)

    settings = config.settings
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    logins = DBSession.query(LoginItem)

    if config.flags.email_type == 'daily':
        logins = logins.filter(LoginItem.time > (datetime.datetime.now() - datetime.timedelta(days=1)))

    if config.flags.email_type == 'weekly':
        logins = logins.filter(LoginItem.time > (datetime.datetime.now() - datetime.timedelta(days=7)))

    if config.flags.email_type == 'monthly':
        logins = logins.filter(LoginItem.time > (datetime.datetime.now() - datetime.timedelta(days=30)))

    if config.flags.email_type == 'invalid':
        logins = logins.filter(LoginItem.time > (datetime.datetime.now() - datetime.timedelta(seconds=3600))).filter(LoginItem.success == False)

    email_text = ''

    by_actor = defaultdict(lambda: defaultdict(list))
    by_location = defaultdict(lambda: defaultdict(list))

    for i in logins.order_by(LoginItem.time.desc()).all():
        actor_text = '{} ({}) at {}'.format(i.location.location, i.ip, i.time)
        location_text = '{} from {} at {}'.format(i.actor.email, i.ip, i.time)

        if not i.success and i.failure:
            actor_text += '. ({})'.format(i.failure)

        by_actor[i.actor.email][i.success].append(actor_text)
        by_location[i.location.location][i.success].append(location_text)


    if len(by_actor.items()) == 0:
        return

    for (k, v) in by_actor.items():
        email_text += '{}\n'.format(k)

        if True in v:
            email_text += '\tValid Logins:\n'
            for i in v[True]:
                email_text += '\t\t{}\n'.format(i)
        if False in v:
            email_text += '\tInvalid Logins:\n'
            for i in v[False]:
                email_text += '\t\t{}\n'.format(i)

        email_text += '\n'

    email_text += '\nLogins by location:\n\n'

    for (k, v) in by_location.items():
        email_text += '{}\n'.format(k)

        if True in v:
            email_text += '\tValid Logins:\n'
            for i in v[True]:
                email_text += '\t\t{}\n'.format(i)
        if False in v:
            email_text += '\tInvalid Logins:\n'
            for i in v[False]:
                email_text += '\t\t{}\n'.format(i)

        email_text += '\n'

    msg = MIMEText(email_text)

    email_to = aslist(config.settings['email.{}'.format(config.flags.email_type)])

    if len(email_to) == 0:
        print "No mailling addresses found for this report. Bailing."

    msg['From'] = config.settings['email.from']
    msg['To'] = ', '.join(email_to)
    msg['Date'] = formatdate()
    msg['Subject'] = '{} status report of account logins'.format(config.flags.email_type)

    mail_server = config.settings['email.server']
    mail_tls = asbool(config.settings['email.tls'])
    mail_from = config.settings['email.from']
    mail_auth_login = config.settings['email.auth.login']
    mail_auth_password = config.settings['email.auth.password']

    smtp = smtplib.SMTP(mail_server)

    if mail_tls:
        smtp.starttls()

    if mail_auth_login:
        smtp.login(mail_auth_login, mail_auth_password)

    smtp.sendmail(mail_from, email_to, msg.as_string())
    smtp.close()

if __name__ == '__main__':
    main()

