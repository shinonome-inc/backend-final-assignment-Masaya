# Generated by Django 4.2 on 2023-04-13 12:15

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("tweets", "0002_tweet_title"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="tweet",
            options={"ordering": ["-created_at"]},
        ),
    ]
