# Generated by Django 4.2.5 on 2024-01-18 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BackEnd', '0016_alter_favorite_game_id_alter_favorite_user_id'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='favorite',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('User_ID', 'Game_ID'), name='composite_primary_key'),
        ),
    ]
