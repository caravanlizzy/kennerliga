# Generated by Django 4.1.2 on 2022-10-31 10:25

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('season', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='player',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]