from reactor import Component

from .models import Functie, Lid, Ouder, Ploeg, PloegLid

class TeamSelector(Component):

    # reference the template from above
    template_name = 'management/components/team-selector.html'

    eligible_players = set({})
    ploegleden = set({})
    ploeg_id = 0

    # deze methode is verantwoordelijk om gegeven een state, de initialisatie te doen
    def mount(self, eligible_players, ploegleden, ploeg_id, **kwargs):
        if eligible_players:
            self.eligible_players = set([Lid.objects.get(pk=lid_id) for lid_id in eligible_players])
        if ploegleden:
            self.ploegleden = set([Lid.objects.get(pk=lid_id) for lid_id in ploegleden])
        self.ploeg_id = ploeg_id

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

    # Receive a delete event
    def receive_verwijder(self, lid, **kwargs):
        self.eligible_players.add(Lid.objects.get(pk=lid))
        self.ploegleden.remove(Lid.objects.get(pk=lid))

    # Receive a submit event
    def receive_indienen(self, **kwargs):
        ploeg = Ploeg.objects.get(ploeg_id=self.ploeg_id)
        # clear the previous team
        PloegLid.objects.filter(ploeg_id=ploeg).delete()

        # insert team members for each player
        functie = Functie.objects.get(functie="Speler")
        insert_ploegleden = [PloegLid(lid_id=lid, ploeg_id=ploeg, functie=functie) for lid in self.ploegleden]
        for pl in insert_ploegleden:
            pl.save()
