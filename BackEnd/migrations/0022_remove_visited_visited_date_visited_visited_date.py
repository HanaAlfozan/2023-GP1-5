# Generated by Django 4.2.5 on 2024-01-29 23:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BackEnd', '0021_visited_visited_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='visited',
            name='Visited_Date',
        ),
        migrations.AddField(
            model_name='visited',
            name='Visited_date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]