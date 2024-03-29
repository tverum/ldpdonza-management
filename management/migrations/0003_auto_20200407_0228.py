# Generated by Django 3.0.5 on 2020-04-07 00:28

import localflavor.generic.models
import phonenumber_field.modelfields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("management", "0002_auto_20200405_0855"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lid",
            name="betalend_lid",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="lid",
            name="email",
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name="lid",
            name="geboortedatum",
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name="lid",
            name="gescheiden_ouders",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="lid",
            name="gsmnummer",
            field=phonenumber_field.modelfields.PhoneNumberField(
                max_length=128, null=True, region=None
            ),
        ),
        migrations.AlterField(
            model_name="lid",
            name="lidnummer_vbl",
            field=models.IntegerField(null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="lid",
            name="rekeningnummer",
            field=localflavor.generic.models.IBANField(
                include_countries=None,
                max_length=34,
                null=True,
                use_nordea_extensions=False,
            ),
        ),
    ]
