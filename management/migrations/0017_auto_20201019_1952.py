# Generated by Django 3.0.5 on 2020-10-19 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0016_betaling_aflossingen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='betaling',
            name='aflossingen',
            field=models.CharField(default='', max_length=500),
        ),
    ]
