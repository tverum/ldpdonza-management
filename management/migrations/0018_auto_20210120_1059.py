# Generated by Django 3.0.11 on 2021-01-20 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("management", "0017_auto_20201019_1952"),
    ]

    operations = [
        migrations.CreateModel(
            name="PloegKenmerk",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("kenmerk", models.CharField(max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name="ploeg",
            name="kenmerken",
            field=models.ManyToManyField(blank=True, to="management.PloegKenmerk"),
        ),
    ]
