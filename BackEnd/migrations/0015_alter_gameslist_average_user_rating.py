# Generated by Django 4.2.7 on 2024-01-20 08:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("BackEnd", "0014_alter_gameslist_age_rating_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="gameslist",
            name="Average_User_Rating",
            field=models.CharField(max_length=255),
        ),
    ]