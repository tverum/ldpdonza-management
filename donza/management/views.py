from bootstrap_modal_forms.generic import BSModalReadView
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, reverse
from django.views import generic
from django.views.generic.edit import FormView, UpdateView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin, MultiTableMixin
from guardian.mixins import PermissionRequiredMixin as GuardianPermissionMixin

from .mail.send_mail import lidgeld_mail
from .main.betalingen import genereer_betalingen
from .main.ledenbeheer import import_from_csv
from .models import Lid, Ploeg, PloegLid, Betaling, Functie
from .resources import CoachLidDownloadResource
# Deze lijn moet er in blijven staan om de TeamSelector te kunnen laden
# noinspection PyUnresolvedReferences
from .visual.components import TeamSelector
from .visual.filters import LidFilter
from .visual.forms import LidForm, OuderForm, PloegForm
from .visual.tables import LidTable, DraftTable, VerstuurdTable

PERMISSION_DENIED = """
            Je hebt niet de juiste permissies om deze pagina te bekijken. 
            Indien je dit wel nodig hebt, contacteer de webmaster. (TODO: add link)
            """


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


class LidEditView(PermissionRequiredMixin, UpdateView):
    template_name = 'management/lid_edit.html'
    template_name_suffix = ""
    form_class = LidForm
    model = Lid
    permission_required = ('management.change_lid',)
    permission_denied_message = PERMISSION_DENIED

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
    permission_required = ('management.view_ploeg',)
    permission_denied_message = PERMISSION_DENIED

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ploegForm"] = PloegForm
        return context


class PloegSelectView(PermissionRequiredMixin, generic.DetailView):
    model = Ploeg
    template_name = 'management/ploeg_select.html'
    permission_required = ('management.change_ploeg',)
    permission_denied_message = PERMISSION_DENIED

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


class PloegView(GuardianPermissionMixin, generic.DetailView):
    model = Ploeg
    template_name = 'management/ploeg_view.html'
    permission_required = ('management.view_ploeg',)
    permission_denied_message = PERMISSION_DENIED
    accept_global_perms = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ploeg = context['object']
        functie_speler = Functie.objects.get(functie="Speler")
        functie_coach = Functie.objects.get(functie="Coach")
        ploegleden = [Lid.objects.get(pk=ploeglid.lid.club_id)
                      for ploeglid in PloegLid.objects.filter(ploeg_id=ploeg.ploeg_id, functie=functie_speler)]
        coaches = [Lid.objects.get(pk=ploeglid.lid.club_id)
                   for ploeglid in PloegLid.objects.filter(ploeg_id=ploeg.ploeg_id, functie=functie_coach)]
        context['ploegleden'] = ploegleden
        context['coaches'] = coaches
        return context


class LidTableView(PermissionRequiredMixin, SingleTableMixin, FilterView):
    model = Lid
    table_class = LidTable
    template_name = 'management/ledenbeheer.html'
    table_pagination = False
    filterset_class = LidFilter
    permission_required = ('management.view_lid',)
    permission_denied_message = PERMISSION_DENIED

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
    permission_denied_message = PERMISSION_DENIED

    def get_tables(self):
        return [
            DraftTable(Betaling.objects.filter(status="draft").all(), prefix="draft-"),
            VerstuurdTable(Betaling.objects.filter(status="mail_sent").all(), prefix="sent-")
        ]


class LidModalView(BSModalReadView):
    model = Lid
    template_name = 'management/lid_modal.html'


def genereer(request):
    if request.method == "POST":
        pks = request.POST.getlist("selection")
        geselecteerde_leden = Lid.objects.filter(pk__in=pks)
        # genereer de betalingen voor de geselecteerde leden
        genereer_betalingen(geselecteerde_leden)

        messages.success(request, "Betalingen voor geselecteerde leden gegenereerd")
        return redirect(reverse("management:leden"), permanent=True)
    else:
        raise Http404("Methode bestaat niet. Deze pagina is niet beschikbaar.")


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
    lidgeld_mail(pk)
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


def export_ploeg(request, pk):
    """
    Export the ploeg to CSV to allow coaches download
    :param request: the initial request
    :param pk: the primary key
    :return: an HTTPResponse containing the CSV-file
    """
    ploeg = Ploeg.objects.get(pk=pk)
    functie_speler = Functie.objects.get(functie="Speler")
    ploegleden = PloegLid.objects.filter(ploeg=ploeg, functie=functie_speler)
    lid_ids = [ploeglid.lid.club_id for ploeglid in ploegleden]
    queryset = Lid.objects.filter(club_id__in=lid_ids)

    download_name = "coach_export_for_{}.csv".format(ploeg.korte_naam)

    coachdownload_resource = CoachLidDownloadResource()
    dataset = coachdownload_resource.export(queryset)
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(download_name)
    return response
