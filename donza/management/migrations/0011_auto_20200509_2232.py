# Generated by Django 3.0.5 on 2020-05-09 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0010_auto_20200503_1732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='functie',
            name='functie',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='lid',
            name='familieleden',
            field=models.ManyToManyField(blank=True, related_name='_lid_familieleden_+', to='management.Lid'),
        ),
        migrations.AlterField(
            model_name='lid',
            name='functies',
            field=models.ManyToManyField(blank=True, to='management.Functie'),
        ),
        migrations.AlterField(
            model_name='lid',
            name='lidnummer_vbl',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
