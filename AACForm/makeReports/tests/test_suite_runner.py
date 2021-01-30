"""
Code adapted from https://gist.github.com/gregsadetsky/5018173

This allows the test suite to run on a Heroku-based test database 
(due to restrictions of Heroku, the standard test runner does not work)
"""
import django
from django.test.runner import DiscoverRunner
from django.conf import settings
from django.core.management import call_command
from django.db.utils import ConnectionHandler

class HerokuTestSuiteRunner(DiscoverRunner):
    """
    Test suite to run from Heroku database
    """
    def setup_databases(self, **kwargs):
        """
        Sets up the database
        """
        ###
        # WARNING: NOT handling 'TEST_MIRROR', 'TEST_DEPENDENCIES'
        ###

        # get new connections to test database
        test_connections = ConnectionHandler(settings.TEST_DATABASES)

        for alias in django.db.connections:
            test_connection = test_connections[alias]

            # set django-wide connection to use test connection
            django.db.connections[alias] = test_connection

            # re-initialize database (this "replaces" the CREATE DATABASE which
            # cannot be issued on Heroku)
            cursor = test_connection.cursor()
            cursor.execute('DROP SCHEMA public CASCADE')
            cursor.execute('CREATE SCHEMA public')

            # code below taken from
            # django.test.simple.DjangoTestSuiteRunner.setup_databases and
            # django.db.backends.creation.create_test_db

            # make them tables
            call_command('migrate',
                        database=test_connection.alias,)

            call_command('flush',
                verbosity=0,
                interactive=False,
                database=test_connection.alias)

    def teardown_databases(self, *args, **kwargs):
        """
        Does nothing, since Heroku database should continue to exist
        """
        # NOP
        pass