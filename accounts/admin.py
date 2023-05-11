from django.contrib import admin

from .models import FollowUser, User

admin.site.register(User)
admin.site.register(FollowUser)
