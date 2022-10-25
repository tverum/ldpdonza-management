# Generated by Django 3.0.5 on 2020-05-17 17:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("management", "0013_auto_20200511_1646"),
    ]

    operations = [
        migrations.CreateModel(
            name="LidgeldKlasse",
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
                ("naam", models.CharField(max_length=20)),
                ("lidgeld", models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name="lid",
            name="afbetaling",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="lid",
            name="facturatie",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="lid",
            name="uid",
            field=models.DecimalField(
                blank=True,
                decimal_places=0,
                max_digits=10,
                null=True,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="ploeg",
            name="geslacht",
            field=models.CharField(
                choices=[("m", "Man"), ("v", "Vrouw"), ("g", "Gemengd")],
                default="m",
                max_length=2,
            ),
        ),
        migrations.CreateModel(
            name="Betaling",
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
                ("origineel_bedrag", models.FloatField()),
                ("afgelost_bedrag", models.FloatField()),
                (
                    "mails_verstuurd",
                    models.CharField(default="", max_length=500),
                ),
                ("mededeling", models.CharField(max_length=20)),
                ("type", models.CharField(max_length=20)),
                ("status", models.CharField(max_length=20)),
                (
                    "lid",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="management.Lid",
                    ),
                ),
                (
                    "seizoen",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="management.Seizoen",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="ploeg",
            name="lidgeldklasse",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="management.LidgeldKlasse",
            ),
        ),
    ]
