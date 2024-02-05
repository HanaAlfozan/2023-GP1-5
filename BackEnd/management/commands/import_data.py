import csv
from django.core.management.base import BaseCommand
from BackEnd.models import GamesList

class Command(BaseCommand):
    help = 'Import data from CSV file'

    def handle(self, *args, **options):
        csv_file_path = "data/output2.csv"

        with open(csv_file_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                games = GamesList(
                    URL=row['URL'],
                    Name=row['Name'],
                    Icon_URL=row['Icon URL'],
                    Average_User_Rating=row['Average User Rating'],
                    User_Rating_Count=row['User Rating Count'],
                    Price=row['Price'],
                    In_app_Purchases=row['In-app Purchases'],
                    Description=row['Description'],
                    Developer=row['Developer'],
                    Age_Rating=row['Age Rating'],
                    Languages=row['Languages'],
                    Size=row['Size'],
                    Genres=row['Genres'],
                    Original_Release_Date=row['Original Release Date']
                )
                games.save()