# Generated by Django 4.2.1 on 2023-05-24 16:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=88, unique=True)),
                ('platform', models.CharField(choices=[('BGA', 'BGA'), ('Yucata', 'Yucata')], default='BGA', max_length=6)),
            ],
        ),
        migrations.CreateModel(
            name='GameOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=88)),
                ('value', models.BooleanField(default=None, null=True)),
                ('game', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='options', to='game.game')),
            ],
        ),
        migrations.CreateModel(
            name='GameOptionChoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=139, null=True)),
                ('is_active', models.BooleanField(default=False)),
                ('option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='game.gameoption')),
            ],
        ),
    ]
