from django.db import models

from phonenumber_field.modelfields import PhoneNumberField
from localflavor.generic.models import IBANField


class Functie(models.Model):

    functie_id = models.AutoField(primary_key=True)
    functie = models.CharField(max_length=20)

    def __str__(self):
        return self.functie


class Ouder(models.Model):

    ouder_id = models.AutoField(primary_key=True)
    gsmnummer = PhoneNumberField()
    voornaam = models.CharField(max_length=20)
    familienaam = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)

    def __str__(self):
        return self.voornaam + " " + self.familienaam


class Lid(models.Model):

    MAN = "m"
    VROUW = "v"
    ANDER = "x"
    GESLACHT_CHOICES = [
        (MAN, "Man"),
        (VROUW, "Vrouw"),
        (ANDER, "Verkies niet te zeggen"),
    ]

    HEADER_NAMEN = [
        "#",
        "Voornaam",
        "Familienaam",
        "Geslacht",
        "Betalend?",
        "Functies",
        "Straatnaam",
        "Huisnr.",
        "Bus",
        "Postcode",
        "Gemeente",
        "Geboortedat.",
        "Gsm",
        "Moeder",
        "Vader",
        "Email",
        "Gescheiden?",
        "Extra",
        "Rekeningnr.",
        "VBL",
        "Updated",
        "Created",
    ]

    FIELD_NAMEN = [
        "club_id",
        "voornaam",
        "familienaam",
        "geslacht",
        "betalend_lid",
        "functies",
        "straatnaam",
        "huisnummer",
        "bus",
        "postcode",
        "gemeente",
        "geboortedatum",
        "gsmnummer",
        "moeder_id",
        "vader_id",
        "email",
        "gescheiden_ouders",
        "extra_informatie",
        "rekeningnummer",
        "lidnummer_vbl",
        "updated_at",
        "created_at",
    ]

    club_id = models.AutoField(primary_key=True)
    voornaam = models.CharField(max_length=20)
    familienaam = models.CharField(max_length=50)
    geslacht = models.CharField(
        max_length=1,
        choices=GESLACHT_CHOICES,
        default=MAN
    )
    betalend_lid = models.BooleanField(default=False)
    functies = models.ManyToManyField('management.Functie')
    straatnaam = models.CharField(max_length=50)
    huisnummer = models.IntegerField()
    bus = models.CharField(max_length=50, blank=True)
    postcode = models.IntegerField()
    gemeente = models.CharField(max_length=50)
    geboortedatum = models.DateField(null=True)
    gsmnummer = PhoneNumberField(null=True)
    moeder_id = models.ForeignKey(
        'management.Ouder', related_name='moeder', on_delete=models.SET_NULL, null=True)
    vader_id = models.ForeignKey(
        'management.Ouder', related_name='vader', on_delete=models.SET_NULL, null=True)
    email = models.EmailField(max_length=254, null=True)
    gescheiden_ouders = models.BooleanField(default=False)
    extra_informatie = models.CharField(default="", max_length=500, blank=True)
    # TODO: determine if this is really required
    # rijksregisternummer = models.CharField(max_length=20)
    rekeningnummer = IBANField(null=True)
    lidnummer_vbl = models.IntegerField(null=True, unique=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {} - ({})".format(self.voornaam, self.familienaam, self.lidnummer_vbl)
