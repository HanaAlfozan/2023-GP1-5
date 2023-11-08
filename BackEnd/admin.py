from django.contrib import admin
from .models import GGUser

admin.site.register(GGUser) 

list_display = ('Username', 'Email','Password')