# Generated by Django 3.0.5 on 2020-05-14 21:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0014_auto_20200514_0135'),
    ]

    operations = [
        migrations.CreateModel(
            name='LidgeldKlasse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('naam', models.CharField(max_length=20)),
                ('lidgeld', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='ploeg',
            name='lidgeldklasse',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='management.LidgeldKlasse'),
        ),
    ]
