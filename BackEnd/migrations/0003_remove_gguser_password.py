# Generated by Django 4.2.5 on 2023-11-06 02:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('BackEnd', '0002_gguser_delete_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gguser',
            name='Password',
        ),
    ]
