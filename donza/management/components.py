from reactor import Component

from .models import Functie, Lid, Ouder, Ploeg, PloegLid

class TeamSelector(Component):

    # reference the template from above
    template_name = 'management/components/team-selector.html'

    eligible_players = set({})
    ploegleden = set({})
    ploeg_id = 0

    # This method is called after __init__ passing the initial state of the
    # Component, this method is responsible taking the state of the component
    # and construct or reconstruct the component. Sometimes loading things from
    # the database like tests of this project.
    def mount(self, eligible_players, ploegleden, ploeg_id, **kwargs):
        if eligible_players:
            self.eligible_players.update([Lid.objects.get(pk=lid_id) for lid_id in eligible_players])
        if ploegleden:
            self.ploegleden.update([Lid.objects.get(pk=lid_id) for lid_id in ploegleden])
        self.ploeg_id = ploeg_id

    # This method is used to capture the essence of the state of a component
    # state, so it can be reconstructed at any given time on the future.
    # By passing what ever is returned by this method to `mount`.
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
        functie = Functie.objects.get(functie="Speler")
        ploeg = Ploeg.objects.get(ploeg_id=self.ploeg_id)
        insert_ploegleden = [PloegLid(lid_id=lid, ploeg_id=ploeg, functie=functie) for lid in self.ploegleden]
        for pl in insert_ploegleden:
            pl.save()
