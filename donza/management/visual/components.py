import datetime

from reactor import Component

from donza.management.models import Functie, Lid, Ouder, Ploeg, PloegLid, MAN, VROUW


class TeamSelector(Component):

    # reference the template from above
    template_name = 'management/components/team-selector.html'

    eligible_players = set([])
    ploegleden = set([])
    display_players = set([])
    ploeg_id = 0
    showall = False
    message = []

    # deze methode is verantwoordelijk om gegeven een state, de initialisatie te doen
    def mount(self, eligible_players, ploegleden, ploeg_id, **kwargs):
        self.ploeg_id = ploeg_id
        if not ploegleden:
            ploegleden = [ploeglid.lid.club_id for ploeglid in PloegLid.objects.filter(ploeg=ploeg_id)]
        self.ploegleden = set([Lid.objects.get(pk=lid) for lid in ploegleden])

        if eligible_players:
            self.eligible_players = set([Lid.objects.get(pk=lid_id) for lid_id in eligible_players])
        else:
            self.get_eligible_players(ploeg_id)

        self.get_display_players()

    def get_display_players(self):
        if self.showall:
            self.display_players = self.eligible_players
        else:
            ploeg = Ploeg.objects.get(ploeg_id=self.ploeg_id)
            max_jaar = ploeg.max_geboortejaar
            self.display_players = [lid for lid in self.eligible_players if lid.geboortedatum.year < max_jaar]

    def get_eligible_players(self, ploeg_id):
        ploeg = Ploeg.objects.get(pk=ploeg_id)
        max_jaar = ploeg.uitzonderings_geboortejaar
        min_jaar = ploeg.min_geboortejaar
        if ploeg.geslacht in [MAN, VROUW]:
            if min_jaar:
                self.eligible_players = Lid.objects.all() \
                    .filter(
                        sportief_lid=True,
                        geslacht=ploeg.geslacht
                    ) \
                    .exclude(geboortedatum=None) \
                    .filter(
                        geboortedatum__year__lte=max_jaar,
                        geboortedatum__year__gte=min_jaar
                    )
            else:
                self.eligible_players = Lid.objects.all() \
                    .filter(
                        sportief_lid=True,
                        geslacht=ploeg.geslacht
                    ) \
                    .exclude(geboortedatum=None) \
                    .filter(
                        geboortedatum__year__lte=max_jaar
                    )
        else:
            if min_jaar:
                self.eligible_players = Lid.objects.all() \
                    .filter(
                        sportief_lid=True
                    ) \
                    .exclude(geboortedatum=None) \
                    .filter(
                        geboortedatum__year__lte=max_jaar,
                        geboortedatum__year__gte=min_jaar
                    )
            else:
                self.eligible_players = Lid.objects.all() \
                    .filter(
                        sportief_lid=True
                    ) \
                    .exclude(geboortedatum=None) \
                    .filter(
                        geboortedatum__year__lte=max_jaar
                    )

    # deze methode is verantwoordelijk om de essentie van de state te capturen
    def serialize(self):
        ep = [player.club_id for player in self.eligible_players]
        pl = [player.club_id for player in self.ploegleden]
        ploeg_id = self.ploeg_id
        return dict(id=self.id, eligible_players=ep, ploegleden=pl, ploeg_id=ploeg_id)

    # This are the event handlers they always start with `receive_`

    # Receive an add event
    def receive_voegtoe(self, lid, **kwargs):
        self.eligible_players.remove(Lid.objects.get(pk=lid))
        self.ploegleden.add(Lid.objects.get(pk=lid))
        self.get_display_players()

    # Receive a delete event
    def receive_verwijder(self, lid, **kwargs):
        self.eligible_players.add(Lid.objects.get(pk=lid))
        self.ploegleden.remove(Lid.objects.get(pk=lid))
        self.get_display_players()

    # Receive a submit event
    def receive_indienen(self, **kwargs):
        ploeg = Ploeg.objects.get(ploeg_id=self.ploeg_id)
        # clear the previous team
        PloegLid.objects.filter(ploeg_id=ploeg).delete()

        try:
            # insert team members for each player
            functie = Functie.objects.get(functie="Speler")
        except Functie.DoesNotExist:
            self.message = 'Functie "Speler" is nog niet gedefinieerd.'
            return

        insert_ploegleden = [PloegLid(lid_id=lid.club_id, ploeg_id=ploeg.ploeg_id, functie=functie) for lid in self.ploegleden]
        for pl in insert_ploegleden:
            pl.save()
        print("Opslaan geslaagd")

    def receive_showall(self, **kwargs):
        self.showall = not self.showall
        self.get_display_players()
