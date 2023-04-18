from django.db import models

from accounts.models import User


class Tweet(models.Model):
    title = models.CharField(max_length=30, null=True)
    content = models.CharField(max_length=150)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]
