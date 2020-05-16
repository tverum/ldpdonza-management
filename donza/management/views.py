from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import redirect, reverse
from django.views import generic
from django.views.generic.edit import FormView, UpdateView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin, MultiTableMixin
from django.http import Http404

from .main.betalingen import genereer_betalingen
from .main.ledenbeheer import import_from_csv
from .models import Lid, Ploeg, PloegLid, Betaling, Functie
# Deze lijn moet er in blijven staan om de TeamSelector te kunnen laden
# noinspection PyUnresolvedReferences
from .visual.components import TeamSelector
from .visual.filters import LidFilter
from .visual.forms import LidForm, OuderForm, PloegForm
from .visual.tables import LidTable, DraftTable, VerstuurdTable


class IndexView(generic.TemplateView):
    template_name = "management/index.html"


class LidNewView(FormView):
    template_name = 'management/lid_edit.html'
    form_class = LidForm
    model = Lid

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ouderform"] = OuderForm
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("management:leden")


class LidEditView(UpdateView):
    template_name = 'management/lid_edit.html'
    template_name_suffix = ""
    form_class = LidForm
    model = Lid

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ouderform"] = OuderForm
        return context

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse("management:leden")


class PloegListView(PermissionRequiredMixin, generic.ListView):
    model = Ploeg
    template_name = "management/ploeg_list.html"
    permission_required = ('ploeg.can_view',)
    permission_denied_message = """
        Je hebt niet de juiste permissies om deze pagina te bekijken. 
        Indien je dit wel nodig hebt, contacteer de webmaster. (TODO: add link)
        """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ploegForm"] = PloegForm
        return context


class PloegSelectView(generic.DetailView):
    model = Ploeg
    template_name = 'management/ploeg_select.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ploeg = context['object']
        ploegleden = self.get_ploegleden(ploeg)
        context['eligible_players'] = self.get_eligible_players(
            ploeg, ploegleden)
        context['ploegleden'] = ploegleden
        context['ploeg_id'] = ploeg.ploeg_id
        ploegcoaches = self.get_ploegcoaches(ploeg)
        print(ploegcoaches)
        context['ploegcoaches'] = ploegcoaches
        context['coaches'] = self.get_coaches(ploegcoaches)
        return context

    @staticmethod
    def get_eligible_players(ploeg, ploegleden):
        max_jaar = ploeg.uitzonderings_geboortejaar
        min_jaar = ploeg.min_geboortejaar
        if min_jaar:
            queryset = Lid.objects.all() \
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
            queryset = Lid.objects.all() \
                .filter(
                sportief_lid=True,
                geslacht=ploeg.geslacht
            ) \
                .exclude(geboortedatum=None) \
                .filter(
                geboortedatum__year__lte=max_jaar
            )
        ep = [lid.club_id for lid in queryset if not lid.club_id in ploegleden]
        return ep

    @staticmethod
    def get_ploegleden(ploeg):
        functie = Functie.objects.get(functie="Speler")
        leden_ids = [ploeglid.lid.club_id for ploeglid in PloegLid.objects.filter(
            ploeg_id=ploeg.ploeg_id, functie=functie)]
        return leden_ids

    @staticmethod
    def get_ploegcoaches(ploeg):
        functie = Functie.objects.get(functie="Coach")
        coach_ids = [ploeglid.lid.club_id for ploeglid in PloegLid.objects.filter(
            ploeg_id=ploeg.ploeg_id, functie=functie)]
        return coach_ids

    @staticmethod
    def get_coaches(ploegcoaches):
        functie = Functie.objects.get(functie="Coach")
        queryset = Lid.objects.filter(functies__functie=functie)
        coaches = [lid.club_id for lid in queryset if lid.club_id not in ploegcoaches]
        print(coaches)
        return coaches


class PloegView(generic.DetailView):
    model = Ploeg
    template_name = 'management/ploeg_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ploeg = context['object']
        ploegleden = [Lid.objects.get(pk=ploeglid.lid.club_id)
                      for ploeglid in PloegLid.objects.filter(ploeg_id=ploeg.ploeg_id)]
        context['ploegleden'] = ploegleden
        return context


class LidTableView(PermissionRequiredMixin, SingleTableMixin, FilterView):
    model = Lid
    table_class = LidTable
    template_name = 'management/ledenbeheer.html'
    table_pagination = False
    filterset_class = LidFilter
    permission_required = ('management.view_lid',)
    permission_denied_message = """
        Je hebt niet de juiste permissies om deze pagina te bekijken. 
        Indien je dit wel nodig hebt, contacteer de webmaster. (TODO: add link)
        """

    def post(self, request, *args, **kwargs):
        # retrieve the file from the request
        csv_file = request.FILES['file']

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "This is not a csv file")
            redirect(reverse("management:leden"), permanent=True)

        import_from_csv(csv_file, request)
        messages.success(request, "Import van csv succesvol")

        return redirect(reverse("management:leden"), permanent=True)


class BetalingTableView(PermissionRequiredMixin, MultiTableMixin, generic.TemplateView):
    model = Betaling
    permission_required = ('management.view_betaling',)
    template_name = 'management/betalingen.html'
    permission_denied_message = """
        Je hebt niet de juiste permissies om deze pagina te bekijken. 
        Indien je dit wel nodig hebt, contacteer de webmaster. (TODO: add link)
        """
    tables = [
        DraftTable(Betaling.objects.filter(status="draft").all(), prefix="draft-"),
        VerstuurdTable(Betaling.objects.filter(status="mail_sent").all(), prefix="sent-")
    ]


def genereer(request):
    if request.method == "POST":
        pks = request.POST.getlist("selection")
        geselecteerde_leden = Lid.objects.filter(pk__in=pks)
        # genereer de betalingen voor de geselecteerde leden
        genereer_betalingen(geselecteerde_leden)

        messages.success(request, "Betalingen voor geselecteerde leden gegenereerd")
        return redirect(reverse("management:leden"), permanent=True)
    else:
        # no idea what to do here
        print("Test")
        pass


def create_ouder(request):
    lid_form = LidForm(request.POST.get("lid_form"))
    ouder_form = OuderForm(request.POST)
    redirect_path = request.POST.get("next")
    context = {
        'form': lid_form,
    }
    if ouder_form.is_valid():
        ouder_form.save()
    else:
        messages.add_message(request, messages.ERROR,
                             ouder_form.errors)
    return redirect(redirect_path)


def create_ploeg(request):
    ploeg_form = PloegForm(request.POST)
    redirect_path = request.POST.get("next")
    if ploeg_form.is_valid():
        ploeg_form.save()
    else:
        messages.add_message(request, messages.ERROR,
                             "Ongeldig formulier voor nieuwe ploeg")
    return redirect(redirect_path)


def stuur_mail(_, pk):
    send_mail(
        "Test onderwerp voor pk: {}".format(pk),
        "Test message",
        from_email="no-reply@ldpdonza.be",
        recipient_list=["vanerum.tim@icloud.com", ]
    )
    return redirect(reverse("management:betalingen"), permanent=False)


def verwijder_lid(_, pk):
    Lid.objects.get(pk=pk).delete()
    return redirect(reverse("management:leden"), permanent=False)


def verwijder_leden(request):
    if request.method == "POST":
        pks = request.POST.getlist("selection")
        geselecteerde_leden = Lid.objects.filter(pk__in=pks)

        geselecteerde_leden.all().delete()

        messages.success(request, "Geselecteerde leden verwijderd")
        return redirect(reverse("management:leden"), permanent=True)
    else:
        # no idea what to do here
        print("Test")
        pass


def verwerk_leden(request):
    if request.method == "POST":
        if 'verwijder' in request.POST:
            return verwijder_leden(request)
        elif 'genereer' in request.POST:
            return genereer(request)
        else:
            raise Http404("Action not found")
    else:
        # no idea what to do here
        print("Test")
        pass
