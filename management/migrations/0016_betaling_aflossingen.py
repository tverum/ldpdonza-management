# Generated by Django 3.0.5 on 2020-08-04 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("management", "0015_auto_20200521_2001"),
    ]

    operations = [
        migrations.AddField(
            model_name="betaling",
            name="aflossingen",
            field=models.CharField(blank=True, default="", max_length=500, null=True),
        ),
    ]
