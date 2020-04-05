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

    club_id = models.AutoField(primary_key=True)
    voornaam = models.CharField(max_length=20)
    familienaam = models.CharField(max_length=50)
    geslacht = models.CharField(
        max_length=1,
        choices=GESLACHT_CHOICES,
        default=MAN
    )
    betalend_lid = models.BooleanField(default=False, help_text="Dit moet waar zijn als het lid lidgeld moet betalen")
    functies = models.ManyToManyField('management.Functie')
    straatnaam = models.CharField(max_length=50)
    huisnummer = models.IntegerField()
    bus = models.CharField(max_length=50, blank=True)
    postcode = models.IntegerField()
    gemeente = models.CharField(max_length=50)
    geboortedatum = models.DateField()
    gsmnummer = PhoneNumberField()
    moeder_id = models.ForeignKey('management.Ouder', related_name='moeder', on_delete=models.SET_NULL, null=True)
    vader_id = models.ForeignKey('management.Ouder', related_name='vader', on_delete=models.SET_NULL, null=True)
    email = models.EmailField(max_length=254)
    gescheiden_ouders = models.BooleanField(default=False, help_text="Voor gescheiden ouders worden de mails standaard naar beide ouders gestuurd")
    extra_informatie = models.CharField(default="", max_length=500, blank=True)
    # TODO: determine if this is really required
    # rijksregisternummer = models.CharField(max_length=20)
    rekeningnummer = IBANField()
    lidnummer_vbl = models.IntegerField(unique=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {} - ({})".format(self.voornaam, self.familienaam, self.lidnummer_vbl)





