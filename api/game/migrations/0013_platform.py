# Generated by Django 5.0.4 on 2024-05-16 15:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('game', '0012_startingpointsystem_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
    ]
