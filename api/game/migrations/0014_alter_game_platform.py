# Generated by Django 5.0.4 on 2024-05-16 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0013_platform'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='platform',
            field=models.CharField(max_length=255),
        ),
    ]
