# Generated by Django 4.2.7 on 2024-04-27 17:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("BackEnd", "0027_filtered_game_sorted_game_delete_filtered_games_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Filtered_Games",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("URL", models.TextField()),
                ("Name", models.TextField()),
                ("Icon_URL", models.TextField()),
                ("ID", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Sorted_Games",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("URL", models.TextField()),
                ("Name", models.TextField()),
                ("Icon_URL", models.TextField()),
                ("ID", models.IntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name="sorted_game",
            name="ID",
        ),
        migrations.DeleteModel(
            name="filtered_game",
        ),
        migrations.DeleteModel(
            name="sorted_game",
        ),
    ]
