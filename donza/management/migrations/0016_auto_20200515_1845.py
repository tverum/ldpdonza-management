# Generated by Django 3.0.5 on 2020-05-15 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0015_auto_20200514_2304'),
    ]

    operations = [
        migrations.AddField(
            model_name='lid',
            name='afbetaling',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='lid',
            name='facturatie',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='lid',
            name='uid',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='betaling',
            name='mails_verstuurd',
            field=models.CharField(default='', max_length=500),
        ),
    ]