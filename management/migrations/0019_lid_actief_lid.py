# Generated by Django 3.0.11 on 2021-06-16 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("management", "0018_auto_20210120_1059"),
    ]

    operations = [
        migrations.AddField(
            model_name="lid",
            name="actief_lid",
            field=models.BooleanField(default=True),
        ),
    ]
