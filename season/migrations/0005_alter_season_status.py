# Generated by Django 4.1.2 on 2023-05-20 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('season', '0004_alter_season_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='season',
            name='status',
            field=models.CharField(choices=[('Nächste', 'Next'), ('Anmeldung offen', 'Open'), ('Läuft', 'Running'), ('Beendet', 'Done')], default='Nächste', max_length=15),
        ),
    ]