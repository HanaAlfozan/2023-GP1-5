# Generated by Django 4.2.5 on 2023-11-16 14:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('BackEnd', '0008_remove_gguser_is_active_remove_gguser_is_staff'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gguser',
            name='is_superuser',
        ),
        migrations.RemoveField(
            model_name='gguser',
            name='last_login',
        ),
    ]
