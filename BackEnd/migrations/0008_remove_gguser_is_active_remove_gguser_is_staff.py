# Generated by Django 4.2.5 on 2023-11-16 14:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('BackEnd', '0007_alter_gguser_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gguser',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='gguser',
            name='is_staff',
        ),
    ]