import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


# using postgres with docker-compose in django app,
# django app sometimes fails to start with database Error
# once the postgres service is started there are few extra set up
# tasks that need to be done on postgress
# before it is ready to except connection, that means that django
# will start to connect to postgres before
# it is ready, and then it will fail
# with Error connection and we will be forced to restart

class Command(BaseCommand):
    """
    Django command to pause execution until database is available
    """

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write(
                    'database unavailable, waiting 1 second ....'
                    )
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('database available!'))
