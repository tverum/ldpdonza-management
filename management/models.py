import logging
from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from localflavor.generic.models import IBANField
from phonenumber_field.modelfields import PhoneNumberField

MAN = "m"
VROUW = "v"
ANDER = "x"
GEMENGD = "g"
LID_GESLACHT_CHOICES = [
    (MAN, "Man"),
    (VROUW, "Vrouw"),
    (ANDER, "Verkies niet te zeggen"),
]
PLOEG_GESLACHT_CHOICES = [
    (MAN, "Man"),
    (VROUW, "Vrouw"),
    (GEMENGD, "Gemengd"),
]

logger = logging.getLogger(__name__)


class Functie(models.Model):
    functie_id = models.AutoField(primary_key=True)
    functie = models.CharField(max_length=50)
    objects = models.Manager()

    def __str__(self):
        return self.functie


class Ouder(models.Model):
    ouder_id = models.AutoField(primary_key=True)
    gsmnummer = PhoneNumberField()
    voornaam = models.CharField(max_length=20)
    familienaam = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    objects = models.Manager()

    def __str__(self):
        return self.voornaam + " " + self.familienaam


class Seizoen(models.Model):
    seizoen_id = models.AutoField(primary_key=True)
    naam = models.CharField(max_length=20)
    startdatum = models.DateField()
    einddatum = models.DateField()
    bezig = models.BooleanField()
    objects = models.Manager()

    def __str__(self):
        return "({}-{})".format(self.startdatum.year, self.einddatum.year)


class PloegKenmerk(models.Model):
    kenmerk = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.kenmerk


class Ploeg(models.Model):
    ploeg_id = models.AutoField(primary_key=True)
    seizoen = models.ForeignKey("management.Seizoen", on_delete=models.CASCADE)
    naam = models.CharField(max_length=20)
    korte_naam = models.CharField(max_length=5)
    min_geboortejaar = models.IntegerField(null=True, blank=True)
    max_geboortejaar = models.IntegerField()
    uitzonderings_geboortejaar = models.IntegerField()
    geslacht = models.CharField(
        max_length=2, choices=PLOEG_GESLACHT_CHOICES, default=MAN
    )
    lidgeldklasse = models.ForeignKey(
        "management.LidgeldKlasse",
        default=None,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
    )
    objects = models.Manager()
    kenmerken = models.ManyToManyField(PloegKenmerk, blank=True)

    def __str__(self):
        return "({}) {} ({}-{})".format(
            self.geslacht,
            self.naam,
            self.seizoen.startdatum.year,
            self.seizoen.einddatum.year,
        )


class PloegLid(models.Model):
    ploeg = models.ForeignKey("management.Ploeg", on_delete=models.CASCADE)
    lid = models.ForeignKey("management.Lid", on_delete=models.CASCADE)
    functie = models.ForeignKey("management.Functie", on_delete=models.CASCADE)
    objects = models.Manager()

    def __str__(self):
        return "Ploeg: {} -- Lid: {} ({})".format(
            self.ploeg, self.lid, self.functie
        )

    def clean(self) -> None:
        """
        Clean method. Called during validation of the model during instance creation.
        Overwritten to implement custom validation logic.

        Raises:
            ValidationError: Raises a ValidationError when validation fails
        """
        if (
            self.ploeg.geslacht != "g"
            and self.ploeg.geslacht != self.lid.geslacht
        ):
            raise ValidationError(
                f"Lid {self.lid.voornaam} {self.lid.familienaam} kan \
                    niet in ploeg {self.ploeg.naam} zitten, aangezien \
                        het lid het verkeerde geslacht heeft."
            )

        if (
            not self.ploeg.min_geboortejaar
            <= self.lid.geboortedatum.year
            <= self.ploeg.uitzonderings_geboortejaar
        ):
            raise ValidationError(
                f"Lid {self.lid.voornaam + ' ' + self.lid.familienaam} kan \
                    niet in ploeg {self.ploeg.naam} zitten, aangezien het \
                        lid niet de correcte leeftijd heeft."
            )

    def save(self, *args, **kwargs):
        """
        Overwrite the save method to include a full validation

        Returns:
            _type_: _description_
        """
        self.full_clean()
        return super().save(*args, **kwargs)


class Lid(models.Model):
    club_id = models.AutoField(primary_key=True)
    voornaam = models.CharField(max_length=20)
    familienaam = models.CharField(max_length=50)
    geslacht = models.CharField(
        max_length=1, choices=LID_GESLACHT_CHOICES, default=MAN
    )
    sportief_lid = models.BooleanField(default=False)
    betalend_lid = models.BooleanField(default=False)
    actief_lid = models.BooleanField(default=True)
    straatnaam_en_huisnummer = models.CharField(max_length=50)
    postcode = models.IntegerField()
    gemeente = models.CharField(max_length=50)
    geboortedatum = models.DateField(null=True)
    gsmnummer = PhoneNumberField(null=True, blank=True)
    moeder = models.ForeignKey(
        "management.Ouder",
        related_name="moeder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    vader = models.ForeignKey(
        "management.Ouder",
        related_name="vader",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    email = models.EmailField(max_length=254, null=True, blank=True)
    gescheiden_ouders = models.BooleanField(default=False)
    extra_informatie = models.CharField(default="", max_length=500, blank=True)
    rekeningnummer = IBANField(null=True, blank=True)
    lidnummer_vbl = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    functies = models.ManyToManyField(Functie, blank=True)
    familieleden = models.ManyToManyField("self", blank=True)
    facturatie = models.BooleanField(default=False)
    afbetaling = models.BooleanField(default=False)
    uid = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        unique=True,
        blank=True,
        null=True,
    )
    objects = models.Manager()

    def __str__(self):
        return f"{self.voornaam} {self.familienaam} ({self.lidnummer_vbl})"


class Betaling(models.Model):
    origineel_bedrag = models.FloatField()
    afgelost_bedrag = models.FloatField()
    lid = models.ForeignKey("management.Lid", on_delete=models.CASCADE)
    seizoen = models.ForeignKey("management.Seizoen", on_delete=models.CASCADE)
    mails_verstuurd = models.CharField(
        max_length=500, default="", null=True, blank=True
    )
    mededeling = models.CharField(max_length=20)
    type = models.CharField(max_length=20)
    # TODO: make this a dynamic field
    status = models.CharField(max_length=20)
    aflossingen = models.CharField(max_length=500, default="")
    objects = models.Manager()

    def __str__(self):
        return "{}: {}".format(self.lid, self.mededeling)

    def los_af(self, aflossing):
        """
        Los een betaling af
        :param aflossing:
        :return:
        """
        afl_nummers = self.aflossingen.split(",")
        datum = datetime.strftime(
            datetime.strptime(aflossing["datum"], "%d/%m/%Y"), "%d/%m/%Y"
        )

        if datum not in afl_nummers:
            bedrag = aflossing["credit"].replace(",", ".")
            self.afgelost_bedrag += float(bedrag)
            if self.afgelost_bedrag >= self.origineel_bedrag:
                self.status = "betaald"
            afl_nummers.append(datum)
            self.aflossingen = ",".join(afl_nummers)
            self.save()
            return True
        else:
            return False


class LidgeldKlasse(models.Model):
    naam = models.CharField(max_length=20)
    lidgeld = models.IntegerField()
    objects = models.Manager()

    def __str__(self):
        return self.naam
