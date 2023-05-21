# Generated by Django 4.1.2 on 2023-05-20 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('season', '0005_alter_season_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='season',
            name='status',
            field=models.CharField(choices=[('Nächste', 'Next'), ('Anmeldung offen', 'Open'), ('Laufend', 'Running'), ('Beendet', 'Done')], default='Nächste', max_length=15),
        ),
    ]