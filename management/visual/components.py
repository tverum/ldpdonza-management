from django.shortcuts import reverse
from reactor import Component

from ..models import Functie, Lid, Ploeg, PloegLid, MAN, VROUW


class TeamSelector(Component):
    # reference the template from above
    template_name = 'management/components/team-selector.html'

    eligible_players = set([])
    ploegleden = set([])
    display_players = set([])
    ploegcoaches = set([])
    coaches = set([])
    pvn = set([])
    ploegpvn = set([])
    ploeg_id = 0
    showall = False
    message = []

    # deze methode is verantwoordelijk om gegeven een state, de initialisatie te doen
    def mount(self, eligible_players, ploegleden, coaches, ploegcoaches, pvn, ploegpvn, ploeg_id, **kwargs):
        # set ploegid
        self.ploeg_id = ploeg_id

        # Spelers gedeelte
        if not ploegleden:
            functie = Functie.objects.get(functie="Speler")
            ploegleden = [ploeglid.lid.club_id for ploeglid in PloegLid.objects.filter(ploeg=ploeg_id, functie=functie)]
        self.ploegleden = set([Lid.objects.get(pk=lid) for lid in ploegleden])

        if eligible_players:
            self.eligible_players = set([Lid.objects.get(pk=lid_id) for lid_id in eligible_players])
        else:
            self.get_eligible_players(ploeg_id)

        self.get_display_players()

        # Coaches gedeelte
        if not ploegcoaches:
            functie = Functie.objects.get(functie="Coach")
            ploegcoaches = [ploeglid.lid.club_id for ploeglid in
                            PloegLid.objects.filter(ploeg=ploeg_id, functie=functie)]
        self.ploegcoaches = set([Lid.objects.get(pk=lid) for lid in ploegcoaches])

        if coaches:
            self.coaches = set([Lid.objects.get(pk=lid_id) for lid_id in coaches])
        else:
            self.get_coaches()

        # Ploegverantwoordelijken gedeelte
        if not ploegpvn:
            functie = Functie.objects.get(functie="Ploegverantwoordelijke")
            ploegpvn = [ploeglid.lid.club_id for ploeglid in
                        PloegLid.objects.filter(ploeg=ploeg_id, functie=functie)]
        self.ploegpvn = set([Lid.objects.get(pk=lid) for lid in ploegpvn])

        if pvn:
            self.pvn = set([Lid.objects.get(pk=lid_id) for lid_id in pvn])
        else:
            self.get_pvn()

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

    def get_coaches(self):
        coach_functie = Functie.objects.get(functie="Coach")
        self.coaches = Lid.objects.filter(functies__functie=coach_functie).all()

    def get_pvn(self):
        pvn_functie = Functie.objects.get(functie="Ploegverantwoordelijke")
        self.pvn = Lid.objects.filter(functies__functie=pvn_functie).all()

    # deze methode is verantwoordelijk om de essentie van de state te capturen
    def serialize(self):
        ep = [player.club_id for player in self.eligible_players]
        pl = [player.club_id for player in self.ploegleden]
        coaches = [coach.club_id for coach in self.coaches]
        ploegcoaches = [coach.club_id for coach in self.ploegcoaches]
        pvn = [pv.club_id for pv in self.pvn]
        ploegpvn = [ploegpv.club_id for ploegpv in self.ploegpvn]
        ploeg_id = self.ploeg_id
        return dict(id=self.id, eligible_players=ep, ploegleden=pl, coaches=coaches, ploegcoaches=ploegcoaches,
                    pvn=pvn, ploegpvn=ploegpvn, ploeg_id=ploeg_id)

    # This are the event handlers they always start with `receive_`

    # Receive an add event for the lid
    def receive_voegtoe_lid(self, lid, **kwargs):
        self.eligible_players.remove(Lid.objects.get(pk=lid))
        self.ploegleden.add(Lid.objects.get(pk=lid))
        self.get_display_players()

    # Receive an add event for a coach
    def receive_voegtoe_coach(self, coach, **kwargs):
        self.coaches.remove(Lid.objects.get(pk=coach))
        self.ploegcoaches.add(Lid.objects.get(pk=coach))

    # Receive an add event for a ploegverantwoordelijke
    def receive_voegtoe_pv(self, pv, **kwargs):
        self.pvn.remove(Lid.objects.get(pk=pv))
        self.ploegpvn.add(Lid.objects.get(pk=pv))

    # Receive a delete event
    def receive_verwijder_lid(self, lid, **kwargs):
        self.eligible_players.add(Lid.objects.get(pk=lid))
        self.ploegleden.remove(Lid.objects.get(pk=lid))
        self.get_display_players()

    # Receive a delete event
    def receive_verwijder_coach(self, coach, **kwargs):
        self.coaches.add(Lid.objects.get(pk=coach))
        self.ploegcoaches.remove(Lid.objects.get(pk=coach))

    # Receive a delete event
    def receive_verwijder_pv(self, pv, **kwargs):
        self.pvn.add(Lid.objects.get(pk=pv))
        self.ploegpvn.remove(Lid.objects.get(pk=pv))

    # Receive a submit event
    def receive_indienen(self, **kwargs):
        ploeg = Ploeg.objects.get(ploeg_id=self.ploeg_id)
        # clear the previous team
        PloegLid.objects.filter(ploeg_id=ploeg).delete()

        try:
            # insert team members for each player
            functie_speler = Functie.objects.get(functie="Speler")
            functie_coach = Functie.objects.get(functie="Coach")
            functie_pvn = Functie.objects.get(functie="Ploegverantwoordelijke")
        except Functie.DoesNotExist:
            self.message = """
            Functie "Speler", Functie "Coach", Functie "Ploegverantwoordelijke" is nog niet gedefinieerd.
            """
            return

        insert_ploegleden = [PloegLid(lid_id=lid.club_id, ploeg_id=ploeg.ploeg_id, functie=functie_speler) for lid in
                             self.ploegleden]
        insert_ploegcoaches = [PloegLid(lid_id=lid.club_id, ploeg_id=ploeg.ploeg_id, functie=functie_coach) for lid in
                               self.ploegcoaches]
        insert_ploegpvn = [PloegLid(lid_id=lid.club_id, ploeg_id=ploeg.ploeg_id, functie=functie_pvn) for lid in
                               self.ploegpvn]
        for pl in insert_ploegleden:
            pl.save()
        for pl in insert_ploegcoaches:
            pl.save()
        for pl in insert_ploegpvn:
            pl.save()

        self.send_redirect(reverse("management:ploegen"))

    def receive_showall_lid(self, **kwargs):
        self.showall = not self.showall
        self.get_display_players()
