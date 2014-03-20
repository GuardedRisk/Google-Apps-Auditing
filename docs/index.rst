Welcome to acctwatch's documentation!
=====================================

`acctwatch` is a small application that monitors Google Apps for Business
logins for compliance reasons. Using the Google API it fetches the list of
recent logins, stores them to the database. A reporting utility run from
cron then uses the information stored to generate report emails that are sent
to select individuals.

Dependencies
------------

1. Python 2.7
2. virtualenv
3. `libmaxminddb <https://github.com/maxmind/libmaxminddb>`_
4. supervisord

The last item on the list is required to be able to use the GeoIP 2 database
files from maxmind, it is a C library that the Python extension will have to be
able to find to function.

Installation
------------

This installation will take place in `/usr/local/acctwatch/`, if you would like
you can change the location, but be aware you will also need to change that
wherever that path is used below

1. Untar the software

   .. code-block:: sh

      cd /tmp && tar -xf acctwatch.tar.xz

2. Create a new virtual environment

   .. code-block:: sh

        virtualenv /usr/local/acctwatch/

3. Change into the unpacked tar file

   .. code-block:: sh

        cd acctwatch

4. Install the software using pip from the virtual environment:

   .. code-block:: sh

        /usr/local/acctwatch/bin/pip install .

   .. note::

      If this fails to complete successfully, verify that libmaxminddb has been
      installed and is able to be found by the Python module for compilation.

5. Create a new directory for the configuration file

   .. code-block:: sh

        mkdir /usr/local/acctwatch/config/

6. Copy the sample configuration file

   .. code-block:: sh

        cp config/acctwatch.ini.sample /usr/local/acctwatch/config/acctwatch.ini

You may now delete the archive and the directory it was unarchived to.

GeoIP 2 Lite Database Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This project requires that a database containing GeoIP information is
downloaded, maxmind.com makes these available for free from:
http://dev.maxmind.com/geoip/geoip2/geolite2/

You will want to download and gunzip the City database. There is no need to
download the country database too, the city database contains the same
information.


Configuration
-------------

The first thing we need to do is get some credentials by creating a new `google
cloud <http://cloud.google.com>`_ project. Visit
https://cloud.google.com/console to get started.

1. Create a new project, give it a descriptive name and fill out the information
   requested.
2. Click the APIs & auth link for the new project.
3. In the list find Admin SDK, and click the "off" button to turn this feature
   on
4. Under APIs & auth, click the link titled 'credentials'
5. On the right hand side, download the JSON credentials file, and save it as
   `client_secrets.json` in `/usr/local/acctwatch/config/`
6. Modify `acctwatch.ini` to your liking.

   .. note::

      Make sure to update the path to where the GeoIP 2 Lite database is found,
      so that GeoIP information can be found by `acctwatch`.


Initialise acctwatch
--------------------

Using the configuration file above, we need to create the database, and get the
credentials for that specific Google Apps for Business account.

In the following examples, there are two sections in the `.ini` file, one named
`[DEFAULT]` and the other `[mygapps]`, if you don't have any section other than
`[DEFAULT]`, you don't need the `--section mygapps` on the following commands.

1. Change directory to the installation location

   .. code-block:: sh

        cd /usr/local/acctwatch

2. Initialise the database

   .. code-block:: sh

        bin/acctwatch_initdb config/acctwatch.ini --section mygapps

3. Check that the configuration is in order

   .. code-block:: sh

        bin/acctwatch_configcheck config/acctwatch.ini --noauth_local_webserver --section mygapps

4. Go to the link presented, and follow the instructions to log in to your
   Google Apps for Domains account, make sure that the account being used has
   Administrator privileges. Copy and paste the authorization code into the
   application, at this point it should print the message:

   `Success!`

Running acctwatch
-----------------

At this point `acctwatch` is ready for use. The best way to run `acctwatch` is
to use `supervisord`, so that if the application stops for some reason it will
be automatically restarted.

Use the following supervisord configuration to start the process:

.. code-block:: ini

   [program:acctwatch]
   command=/usr/local/acctwatch/bin/acctwatch /usr/local/acctwatch/config/acctwatch.ini --section mygapps
   directory=/tmp
   stdout_logfile=/var/log/acctwatch.log
   stdout_logfile_maxbytes=1MB
   stdout_logfile_backups=10

Restart `supervisord` after modifying it's configuration file so that it picks
up on the changes.

Next we want to add a crontab entry that runs the reporting email, using `acctwatch_email`.

Add the following lines to crontab, feel free to modify them to run at
different times if preferred, this way for example instead of getting the
weekly report on Sunday you can tweak it to receive it on Friday.

.. code-block:: text

   # Run the invalid logins report hourly
   0 * * * *  /usr/local/acctwatch/bin/acctwatch_email /usr/local/acctwatch/config/acctwatch.ini --section mygapps --email-type invalid

   # Run the daily reports every day at noon
   0 12 * * * /usr/local/acctwatch/bin/acctwatch_email /usr/local/acctwatch/config/acctwatch.ini --section mygapps --email-type daily

   # Run the weekly reports every Sunday at noon
   0 12 * * 0 /usr/local/acctwatch/bin/acctwatch_email /usr/local/acctwatch/config/acctwatch.ini --section mygapps --email-type weekly

   # Run the monthly reports on the 1st day of the month, at noon
   0 12 1 * * /usr/local/acctwatch/bin/acctwatch_email /usr/local/acctwatch/config/acctwatch.ini --section mygapps --email-type monthly

Configuration Options
---------------------

The only section required in the `.ini` file is the `[DEFAULT]` section, more
sections can be added so that for example a single configuration file can be
used to monitor multiple different Google Apps for Business accounts.

.. code-block:: ini

    [DEFAULT]

The `client_secrets.json` file contains the credentials for your Google Cloud
OAuth 2.0 project. This is what allows you to request permission to get access
to the Admin SDK using OAuth 2.0.

.. code-block:: ini

    secrets = %(here)s/client_secrets.json


Next up is the email accounts to be notified when `acctwatch_email` is run.
This can also be placed into an individual section to override the defaults.

You can add more than one email address per entry, separated by spaces, and all
of those emails will get notified.

.. code-block:: ini

    email.daily = someone@example.net admin@example.net
    email.weekly = watcher@example.net
    email.monthly = admin@example.net compliance@example.net
    email.invalid = badlogins@example.net


The server to send the email with:

.. code-block:: ini

    email.server = smtp.example.net:587
    email.tls = True
    email.auth.login = smtp.example.net
    email.auth.password = auth_pass_here
    email.from = watcher@example.net


How often should `acctwatch` update it's database. This can be set as often as
you would like, however this counts against your Google Cloud Application's
OAuth requests, setting this to less than 5 minutes is not recommended.

.. code-block:: ini

    # This is how often acctwatch should check for new login entries, setting this
    # to anything less than 1 minute (60) doesn't make much sense, since Google
    # won't add new logins to the list here for up to 5 minutes (in testing), this
    # is set to 30 minutes, since this provides enough resolution.

    interval = 1800


The location where the GeoLite2 City database can be found for GeoIP uses.

.. code-block:: ini

    geoip_db = /path/to/GeoLite2-City.mmdb


You can create new sections for each of the different Google Apps for Business
accounts you would like to monitor. This allows you to use the `[DEFAULT]`
settings for multiple different domains. Everything from the `[DEFAULT]`
section can be overridden here.

.. note::

   `%(__name__)s` gets replaced with the name of the section it is placed under.

.. code-block:: ini

    [mygapps]

    credentials = %(here)s/%(__name__)s.secret_credentials.dat
    sqlalchemy.url = sqlite:///%(here)s/%(__name__)s.db_storage.db
