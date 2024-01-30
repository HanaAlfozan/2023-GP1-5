# Generated by Django 4.2.5 on 2024-01-29 13:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BackEnd', '0019_merge_20240123_1531'),
    ]

    operations = [
        migrations.CreateModel(
            name='Visited',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RemoveConstraint(
            model_name='favorite',
            name='composite_primary_key',
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('User_ID', 'Game_ID'), name='unique_favorite_constraint'),
        ),
        migrations.AddField(
            model_name='visited',
            name='Game_ID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BackEnd.gameslist'),
        ),
        migrations.AddField(
            model_name='visited',
            name='User_ID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BackEnd.gguser'),
        ),
        migrations.AddConstraint(
            model_name='visited',
            constraint=models.UniqueConstraint(fields=('User_ID', 'Game_ID'), name='unique_visited_constraint'),
        ),
    ]
