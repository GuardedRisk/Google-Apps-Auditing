import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README')).read()
CHANGES = open(os.path.join(here, 'CHANGES')).read()

requires = [
        'oauth2client',
        'google-api-python-client',
        'sqlalchemy',
        'geoip2[DB]',
        ]

tests_require = []

testing_requires = tests_require + [
    'nose',
    'coverage',
    ]

docs_requires = requires + [
    'sphinx',
    ]

setup(name='acctwatch',
      version='0.0',
      description='acctwatch',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        ],
      author='Bert JW Regeer',
      author_email='bertjw@regeer.org',
      url='',
      keywords='',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='acctwatch.tests',
      install_requires=requires,
      tests_require=tests_require,
      extras_require = {
          'testing': testing_requires,
          'docs': docs_requires,
          },
      entry_points="""\
      [console_scripts]
      acctwatch = acctwatch.acctwatch:main
      acctwatch_configcheck = acctwatch.configcheck:main
      acctwatch_initdb = acctwatch.initdb:main
      acctwatch_destroydb = acctwatch.destroydb:main
      acctwatch_email = acctwatch.sendmail:main
      """,
      )

