from django.db import models
import csv

class Games(models.Model):
    Game_ID = models.AutoField(primary_key=True)
    URL = models.CharField(max_length=255)
    Name = models.CharField(max_length=255)
    Icon_URL = models.CharField(max_length=255)
    Average_user_rating = models.CharField(max_length=10, null=True)
    User_rating_count = models.CharField(max_length=255,null=True, blank=True)
    Price = models.CharField(max_length=255)
    In_app_purchases = models.CharField(max_length=255)
    Description = models.TextField()
    Developer = models.CharField(max_length=255)
    Age_rating = models.CharField(max_length=10)
    Languages = models.CharField(max_length=255)
    Size = models.DecimalField(max_digits=10, decimal_places=2)
    Genres = models.CharField(max_length=255)
    Original_release_date = models.DateField()



def import_data_from_csv(csv_file_path):
    with open(csv_file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            games = Games(
                URL=row['URL'],
                Name=row['Name'],
                Icon_URL=row['Icon URL'],
                Average_user_rating=row['Average User Rating'],
                User_rating_count=row['User Rating Count'],
                Price=row['Price'],
                In_app_purchases=row['In-app Purchases'],
                Description=row['Description'],
                Developer=row['Developer'],
                Age_rating=row['Age Rating'],
                Languages=row['Languages'],
                Size=row['Size'],
                Genres=row['Genres'],
                Original_release_date=row['Original Release Date']
            )
            games.save()

# Call the function to import data from the CSV
import_data_from_csv("data/appstore_games_pre.csv")