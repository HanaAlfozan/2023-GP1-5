from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, Username, Email, Password=None, Accept_conditions=False, **extra_fields):
        if not Email:
            raise ValueError('The Email field must be set')
        Email = self.normalize_email(Email)
        user = self.model(Username=Username, Email=Email, Accept_conditions=Accept_conditions, **extra_fields)
        user.set_password(Password)
        user.save(using=self._db)
        return user

    def create_superuser(self, Username, Email, Password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(Username, Email, Password, **extra_fields)

class GGUser(AbstractBaseUser, PermissionsMixin):
    User_ID = models.AutoField(primary_key=True)
    Username = models.CharField(max_length=50, unique=True)
    Email = models.EmailField(unique=True)
    Accept_conditions = models.BooleanField(default=False)
    First_name = models.CharField(max_length=30)
    Last_name = models.CharField(max_length=30)
    Approved_age_group = models.BooleanField(default=False)
    Age_group = models.CharField(max_length=4, null=True, blank=True)
    Date_joined = models.DateTimeField(auto_now_add=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Specify unique related_name for groups and user_permissions
    groups = models.ManyToManyField('auth.Group', related_name='User', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='User', blank=True)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.Username
