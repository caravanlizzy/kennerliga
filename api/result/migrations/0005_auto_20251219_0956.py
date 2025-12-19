from django.db import migrations

def copy_factions(apps, schema_editor):
    Result = apps.get_model('result', 'Result')
    for result in Result.objects.exclude(faction__isnull=True):
        result.factions.add(result.faction)

def reverse_copy_factions(apps, schema_editor):
    Result = apps.get_model('result', 'Result')
    for result in Result.objects.all():
        result.factions.clear()

class Migration(migrations.Migration):
    dependencies = [
        ('result', '0004_result_factions'),
    ]
    operations = [
        migrations.RunPython(copy_factions, reverse_copy_factions),
    ]