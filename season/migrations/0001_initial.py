# Generated by Django 4.1.2 on 2023-04-09 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('month', models.IntegerField(verbose_name='month in the current year')),
                ('status', models.CharField(choices=[('Angekündigt', 'Announced'), ('Anmeldung offen', 'Open'), ('Beendet', 'Done')], default='Beendet', max_length=15)),
            ],
        ),
    ]
