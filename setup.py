import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README')).read()
CHANGES = open(os.path.join(here, 'CHANGES')).read()

requires = [
        'oauth2client',
        'google-api-python-client',
        ]

requires_with_geoip = requires + [
        'geoip2[DB]',
        ]

tests_require = []

testing_requires =  tests_require + [
    'nose',
    'coverage',
    ]

develop_requires = [
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
          'develop': develop_requires,
          'testing': testing_requires,
          'geoip': requires_with_geoip,
          },
      entry_points="""\
      [console_scripts]
      acctwatch = acctwatch.acctwatch:main
      """,
      )

