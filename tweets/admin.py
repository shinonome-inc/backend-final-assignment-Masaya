from django.contrib import admin

from .models import Tweet, TweetLike

# Register your models here.
admin.site.register(Tweet)
admin.site.register(TweetLike)
