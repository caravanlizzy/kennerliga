# Generated by Django 4.2.1 on 2023-06-01 07:21

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('season', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='season',
            name='participants',
            field=models.ManyToManyField(blank=True, related_name='seasons_participating', to=settings.AUTH_USER_MODEL),
        ),
    ]