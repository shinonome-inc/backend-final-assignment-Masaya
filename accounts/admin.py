from django.contrib import admin

from .models import User
from .models import FollowUser

admin.site.register(User)
admin.site.register(FollowUser)
