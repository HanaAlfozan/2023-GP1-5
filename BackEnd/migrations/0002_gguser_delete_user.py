# Generated by Django 4.2.5 on 2023-11-06 00:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('BackEnd', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GGUser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('User_ID', models.AutoField(primary_key=True, serialize=False)),
                ('Username', models.CharField(max_length=50, unique=True)),
                ('Email', models.EmailField(max_length=254, unique=True)),
                ('Password', models.CharField(max_length=128)),
                ('First_name', models.CharField(max_length=30)),
                ('Last_name', models.CharField(max_length=30)),
                ('Approved_age_group', models.BooleanField(default=False)),
                ('Age_group', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('Date_joined', models.DateTimeField(auto_now_add=True)),
                ('Accept_conditions', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, related_name='User', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='User', to='auth.permission')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='User',
        ),
    ]
