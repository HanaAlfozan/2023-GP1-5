import csv
from django.core.management.base import BaseCommand
from BackEnd.models import GGUser
from django.core.exceptions import ValidationError
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Import users from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='"data/Users.csv"')

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    GGUser.objects.create_user(
                        Username=row['Username'],
                        Email=row['Email'],
                        Password=row['password'],
                        Accept_conditions=row['Accept_conditions'].lower() == 'true',
                        First_name=row['First_name'],
                        Last_name=row['Last_name'],
                        Approved_age_group=row['Approved_age_group'],
                    )
                except (ValidationError, IntegrityError) as e:
                    self.stdout.write(self.style.ERROR(f'Error creating user: {e}'))

        self.stdout.write(self.style.SUCCESS('Users imported successfully'))
