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
    Email = models.EmailField(max_length=50)
    Accept_conditions = models.BooleanField(default=False)
    First_name = models.CharField(max_length=30)
    Last_name = models.CharField(max_length=30)
    Approved_age_group = models.BooleanField(default=False)
    Age_group = models.CharField(max_length=4, null=True, blank=True)
    Date_joined = models.DateTimeField(auto_now_add=True)
    @property
    def is_superuser(self):
        return False


    # Specify unique related_name for groups and user_permissions
    groups = models.ManyToManyField('auth.Group', related_name='User', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='User', blank=True)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.Username

class GamesList(models.Model):
    URL = models.TextField()
    Name = models.TextField()
    Icon_URL = models.TextField()
    Average_User_Rating = models.TextField()
    User_Rating_Count = models.TextField()
    Price = models.TextField()
    In_app_Purchases = models.TextField()
    Description = models.TextField()
    Developer = models.TextField()
    Age_Rating = models.TextField()
    Languages = models.TextField()
    Size = models.DecimalField(max_digits=10, decimal_places=2)
    Genres = models.TextField()
    Original_Release_Date = models.TextField()
    Subtitle_Description = models.TextField()
    ID = models.AutoField(primary_key=True)

    def __str__(self):
        return self.Name
