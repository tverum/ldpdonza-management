# Generated by Django 3.0.5 on 2020-05-03 13:47

from django.db import migrations, models
import django.db.models.deletion
import localflavor.generic.models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ("management", "0006_auto_20200411_1646"),
    ]

    operations = [
        migrations.AddField(
            model_name="lid",
            name="functies",
            field=models.ManyToManyField(
                related_name="_lid_functies_+", to="management.Functie"
            ),
        ),
        migrations.AlterField(
            model_name="lid",
            name="email",
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name="lid",
            name="gsmnummer",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, max_length=128, null=True, region=None
            ),
        ),
        migrations.AlterField(
            model_name="lid",
            name="moeder",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="moeder",
                to="management.Ouder",
            ),
        ),
        migrations.AlterField(
            model_name="lid",
            name="rekeningnummer",
            field=localflavor.generic.models.IBANField(
                blank=True,
                include_countries=None,
                max_length=34,
                null=True,
                use_nordea_extensions=False,
            ),
        ),
        migrations.AlterField(
            model_name="lid",
            name="vader",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="vader",
                to="management.Ouder",
            ),
        ),
        migrations.AlterField(
            model_name="ploeg",
            name="seizoen",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="management.Seizoen"
            ),
        ),
        migrations.AlterField(
            model_name="ploeglid",
            name="functie",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="management.Functie"
            ),
        ),
        migrations.AlterField(
            model_name="ploeglid",
            name="lid_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="management.Lid"
            ),
        ),
        migrations.AlterField(
            model_name="ploeglid",
            name="ploeg_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="management.Ploeg"
            ),
        ),
    ]
