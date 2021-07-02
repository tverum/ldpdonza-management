from datetime import datetime as datetime
from management.mail.group_mail import group_mail
from pprint import pprint
from tempfile import template

from bootstrap_modal_forms.generic import BSModalReadView
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.messages.api import warning
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, reverse, render
from django.template import loader
from django.views import generic
from django.views.generic.edit import FormView, UpdateView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin, MultiTableMixin
from guardian.mixins import PermissionRequiredMixin as GuardianPermissionMixin

from .mail.send_mail import lidgeld_mail, send_herinnering, bevestig_betaling
from .main.betalingen import genereer_betalingen, registreer_betalingen
from .main.ledenbeheer import import_from_csv, lid_update_uid
from .models import Lid, Ploeg, PloegLid, Betaling, Functie, Seizoen
from .resources import CoachLidDownloadResource, create_team_workbook, create_general_workbook
# Deze lijn moet er in blijven staan om de TeamSelector te kunnen laden
# noinspection PyUnresolvedReferences
from .utils import get_current_seizoen
from .visual.components import TeamSelector
from .visual.filters import LidFilter
from .visual.forms import LidForm, OuderForm, PloegForm
from .visual.tables import LidTable, DraftTable, VerstuurdTable, BetaaldTable, PloegTable

PERMISSION_DENIED = """
            Je hebt niet de juiste permissies om deze pagina te bekijken.
            Indien je dit wel nodig hebt, contacteer de webmaster. (TODO: add link)
            """

"""
Class based views
"""


class IndexView(generic.TemplateView):
    template_name = "management/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        aantal_leden = len(Lid.objects.all())
        aantal_spelers = len(
            PloegLid.objects.filter(functie__functie="Speler", ploeg__seizoen=get_current_seizoen(self.request)))
        aantal_coaches = len(
            PloegLid.objects.filter(functie__functie="Coach", ploeg__seizoen=get_current_seizoen(self.request)))
        aantal_pvn = len(PloegLid.objects.filter(functie__functie="Ploegverantwoordelijke",
                                                 ploeg__seizoen=get_current_seizoen(self.request)))
        aantal_ploegen = len(Ploeg.objects.filter(
            seizoen=get_current_seizoen(self.request)))
        aantal_betalingen = len(Betaling.objects.filter(
            seizoen=get_current_seizoen(self.request)))
        aantal_onbetaalde = len(
            Betaling.objects.filter(seizoen=get_current_seizoen(self.request)).exclude(status='voltooid'))
        aantal_draft_betalingen = len(
            Betaling.objects.filter(
                seizoen=get_current_seizoen(self.request), status='draft')
        )
        context_app = {
            'aantal_leden': aantal_leden,
            'aantal_spelers': aantal_spelers,
            'aantal_coaches': aantal_coaches,
            'aantal_pvn': aantal_pvn,
            'aantal_ploegen': aantal_ploegen,
            'aantal_betalingen': aantal_betalingen,
            'aantal_onbetaalde': aantal_onbetaalde,
            'aantal_draft_betalingen': aantal_draft_betalingen
        }
        context = {**context, **context_app}
        return context


class LidNewView(FormView):
    template_name = 'management/lid_edit.html'
    form_class = LidForm
    model = Lid

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ouderform"] = OuderForm
        return context

    def form_valid(self, form):
        nieuw_lid = form.save(commit=False)
        if not nieuw_lid.uid:
            lid_update_uid(nieuw_lid)
            nieuw_lid.save()
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


class PloegListView(PermissionRequiredMixin, SingleTableMixin, generic.ListView):
    model = Ploeg
    table_class = PloegTable
    template_name = "management/ploeg_list.html"
    permission_required = ('management.view_ploeg',)
    permission_denied_message = PERMISSION_DENIED

    def get_table_data(self):
        return super().get_table_data().filter(seizoen=get_current_seizoen(self.request))

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
        context['ploegcoaches'] = ploegcoaches
        context['coaches'] = self.get_coaches(ploegcoaches)
        ploegpvn = self.get_ploegpvn(ploeg)
        context['ploegpvn'] = ploegpvn
        context['pvn'] = self.get_pvn(ploegpvn)
        ploeghhn = self.get_ploeghhn(ploeg)
        context['ploeghhn'] = ploeghhn
        context['hhn'] = self.get_hhn(ploeghhn)
        return context

    @staticmethod
    def get_eligible_players(ploeg, ploegleden):
        max_jaar = ploeg.uitzonderings_geboortejaar
        min_jaar = ploeg.min_geboortejaar
        if min_jaar:
            queryset = Lid.objects.all() \
                .filter(
                sportief_lid=True,
                geslacht=ploeg.geslacht,
                actief_lid=True
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
                geslacht=ploeg.geslacht,
                actief_lid=True
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
        queryset = Lid.objects.filter(functies__functie=functie, actief_lid=True)
        coaches = [
            lid.club_id for lid in queryset if lid.club_id not in ploegcoaches]
        return coaches

    @staticmethod
    def get_ploegpvn(ploeg):
        functie = Functie.objects.get(functie="Ploegverantwoordelijke")
        pvn_ids = [ploeglid.lid.club_id for ploeglid in PloegLid.objects.filter(
            ploeg_id=ploeg.ploeg_id, functie=functie)]
        return pvn_ids

    @staticmethod
    def get_pvn(ploegpvn):
        functie = Functie.objects.get(functie="Ploegverantwoordelijke")
        queryset = Lid.objects.filter(functies__functie=functie, actief_lid=True)
        pvn = [lid.club_id for lid in queryset if lid.club_id not in ploegpvn]
        return pvn

    @staticmethod
    def get_ploeghhn(ploeg):
        functie = Functie.objects.get(functie="Helpende Handen")
        pvn_ids = [ploeglid.lid.club_id for ploeglid in PloegLid.objects.filter(
            ploeg_id=ploeg.ploeg_id, functie=functie)]
        return pvn_ids

    @staticmethod
    def get_hhn(ploeghhn):
        functie = Functie.objects.get(functie="Helpende Handen")
        queryset = Lid.objects.filter(functies__functie=functie, actief_lid=True)
        hhn = [lid.club_id for lid in queryset if lid.club_id not in ploeghhn]
        return hhn


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
        functie_pvn = Functie.objects.get(functie="Ploegverantwoordelijke")
        functie_hh = Functie.objects.get(functie="Helpende Handen")
        ploegleden = [Lid.objects.get(pk=ploeglid.lid.club_id)
                      for ploeglid in PloegLid.objects.filter(ploeg_id=ploeg.ploeg_id, functie=functie_speler)]
        coaches = [Lid.objects.get(pk=ploeglid.lid.club_id)
                   for ploeglid in PloegLid.objects.filter(ploeg_id=ploeg.ploeg_id, functie=functie_coach)]
        pvn = [Lid.objects.get(pk=ploeglid.lid.club_id)
               for ploeglid in PloegLid.objects.filter(ploeg_id=ploeg.ploeg_id, functie=functie_pvn)]
        hhn = [Lid.objects.get(pk=ploeglid.lid.club_id)
               for ploeglid in PloegLid.objects.filter(ploeg_id=ploeg.ploeg_id, functie=functie_hh)]
        context['ploegleden'] = ploegleden
        context['coaches'] = coaches
        context['pvn'] = pvn
        context['hhn'] = hhn
        return context


class LidTableView(PermissionRequiredMixin, SingleTableMixin, FilterView):
    model = Lid
    table_class = LidTable
    template_name = 'management/ledenbeheer.html'
    table_pagination = False
    filterset_class = LidFilter
    permission_required = ('management.view_lid',)
    permission_denied_message = PERMISSION_DENIED

    @staticmethod
    def post(request, *args, **kwargs):
        # retrieve the file from the request
        csv_file = request.FILES['file']

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "This is not a csv file")
            return redirect(reverse("management:leden"), permanent=True)

        import_from_csv(csv_file, request)
        messages.success(request, "Import van csv succesvol")

        return redirect(reverse("management:leden"), permanent=True)


class BetalingTableView(PermissionRequiredMixin, MultiTableMixin, generic.TemplateView):
    model = Betaling
    permission_required = ('management.view_betaling',)
    template_name = 'management/betalingen.html'
    permission_denied_message = PERMISSION_DENIED

    def get_tables(self):
        request = self.request
        seizoen = get_current_seizoen(request)
        draft_queryset = Betaling.objects.filter(
            status="draft", seizoen=seizoen).all()
        verstuurd_queryset = Betaling.objects.filter(
            status="mail_sent", seizoen=seizoen).all()
        betaald_queryset = Betaling.objects.filter(
            status="voltooid", seizoen=seizoen).all()
        return [
            DraftTable(draft_queryset, prefix="draft-"),
            VerstuurdTable(verstuurd_queryset, prefix="sent-"),
            BetaaldTable(betaald_queryset, prefix="betaald-"),
        ]

    @staticmethod
    def post(request, *args, **kwargs):
        # retrieve the file from the request
        csv_file = request.FILES['file']
        if not csv_file.name.endswith(".csv"):
            messages.error(request, "This is not a csv file")
            return redirect(reverse("management:betalingen"))

        registreer_betalingen(csv_file, request)
        messages.success(request, "Inlezen van betalingen succesvol")

        return redirect(reverse("management:betalingen"))


class LidModalView(BSModalReadView):
    model = Lid
    template_name = 'management/lid_modal.html'


class MailView(generic.TemplateView):
    template_name = "management/mailing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['mail_template'] = 'mail/intentiemail.html'
        return context


"""
Method based views
"""


def handler500(request, *args, **argv):
    response = render(request, '500.html', {},
                      status=500)
    return response


def genereer(request):
    if request.method == "POST":
        pks = request.POST.getlist("selection")
        geselecteerde_leden = Lid.objects.filter(pk__in=pks)
        # genereer de betalingen voor de geselecteerde leden
        genereer_betalingen(geselecteerde_leden)

        messages.success(
            request, "Betalingen voor geselecteerde leden gegenereerd")
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


def herinnering_mail(_, pk):
    send_herinnering(pk)
    return redirect(reverse("management:betalingen"), permanent=False)


def bevestig_mail(request, pk):
    bevestig_betaling(pk, request)
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


def export_ploeg_csv(request, pk):
    """
    Export the ploeg to CSV to allow coaches download
    :param request: the initial request (unused)
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
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(
        download_name)
    return response


def export_ploeg_xlsx(request, pk):
    """
    Export the ploeg to Excel to allow coaches download
    :param request: Unused request parameter
    :param pk: the primary key
    :return: an HTTPResponse containing the Excel-file
    """
    ploeg, queryset_coaches, queryset_spelers, queryset_pvn, queryset_hh = retrieve_querysets(
        pk)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename={ploeg}-download-{date}.xlsx'.format(
        ploeg=ploeg.korte_naam,
        date=datetime.now().strftime('%d-%m-%Y'),
    )

    workbook = create_team_workbook(
        queryset_coaches, queryset_spelers, queryset_pvn, queryset_hh
    )

    workbook.save(response)
    return response


def retrieve_querysets(pk):
    """
    Retrieve the querysets corresponding with the primary key.
    Help function for the export to xlsx
    :param pk: the primary key of the team for which the download should be executed
    :return: 
    """
    ploeg = Ploeg.objects.get(pk=pk)
    functie_speler = Functie.objects.get(functie="Speler")
    functie_coach = Functie.objects.get(functie="Coach")
    functie_pv = Functie.objects.get(functie="Ploegverantwoordelijke")
    functie_hh = Functie.objects.get(functie="Helpende Handen")
    ploegleden = PloegLid.objects.filter(ploeg=ploeg, functie=functie_speler)
    coaches = PloegLid.objects.filter(ploeg=ploeg, functie=functie_coach)
    pvn = PloegLid.objects.filter(ploeg=ploeg, functie=functie_pv)
    hhn = PloegLid.objects.filter(ploeg=ploeg, functie=functie_hh)
    lid_ids = [ploeglid.lid.club_id for ploeglid in ploegleden]
    coach_ids = [coach.lid.club_id for coach in coaches]
    pv_ids = [pv.lid.club_id for pv in pvn]
    hh_ids = [hh.lid.club_id for hh in hhn]
    queryset_spelers = Lid.objects.filter(club_id__in=lid_ids)
    queryset_coaches = Lid.objects.filter(club_id__in=coach_ids)
    queryset_pvn = Lid.objects.filter(club_id__in=pv_ids)
    queryset_hh = Lid.objects.filter(club_id__in=hh_ids)
    return ploeg, queryset_coaches, queryset_spelers, queryset_pvn, queryset_hh


def export_ploeg_preview(request):
    """
    After selecting the ploegen to export, save these in the session and proceed to selecting the variables to export
    :param request: request containing the requested teams
    :return:
    """
    # Retrieve the selection of teams to be exported from the request
    pks = request.POST.getlist("selection")

    if not pks:
        messages.warning(
            request, 'Geen ploeg geselecteerd, er is niets om te exporteren')
        return redirect(reverse('management:ploegen'))

    request.session['ploegen'] = pks

    ploegen = list(Ploeg.objects.filter(pk__in=pks))

    # Load the template and show the preview where one can select the fields
    template = loader.get_template("management/ploegen_export.html")
    fields = Lid._meta.get_fields(include_parents=False)
    fields = [field for field in fields if not field.is_relation]
    return HttpResponse(template.render(request=request, context={
        'fields': fields,
        'ploegen': ploegen
    }))


def exporteer_ploegen(request):
    """
    Exporteer the ploegen selected in the previous step
    :param request: the request object
    :return:
    """
    # Retrieve the selected ploegen in the previous screen
    # Retrieve the selected fields from the form
    ploegen = request.session.get('ploegen', [])
    selected_ploegen = list(Ploeg.objects.filter(pk__in=ploegen))
    selected_fields = [
        f for f in request.POST.values() if f.startswith('management')]

    if not selected_fields:
        messages.warning(
            request, 'Geen velden geselecteerd, er is niets om te exporteren')
        return redirect(reverse('management:ploegen'))

    # Create a response with the returned export file
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename=ploegendownload-{date}.xlsx'.format(
        date=datetime.now().strftime('%d-%m-%Y'),
    )

    # Create a workbook which shows the selected fields for the selected ploegen
    workbook = create_general_workbook(selected_ploegen, selected_fields)
    workbook.save(response)
    return response


def change_seizoen(request, pk):
    """
    Change seizoen to display
    :param request: the request with the session
    :param pk: the primary key of the seizoen
    :return:
    """
    request.session['seizoen'] = pk
    return redirect(request.GET.get('next'))


def groep_mail(request):
    """[Mailing endpoint, stuur een mail naar een group mensen.]

    Args:
        request ([ASGIRequest]): [de request naar de endpoint]

    Returns:
        [HttpResponse]: [response]
    """
    seizoen = get_current_seizoen(request)
    required_fields = ['mail-template', 'group', 'subject', 'reply']
    if not all([field in request.POST for field in required_fields]):
        messages.warning(request, """
        Er ontbreken velden om een geldige mail te construeren.
        Zorg er zeker voor dat er een mail-template geselecteerd is, er een groep geselecteerd is om naar te sturen 
        en er een onderwerp en reply veld is ingesteld.
        """)
        return redirect(reverse('management:mails'))
    else:
        group = request.POST.get("group")
        mail_template = request.POST.get("mail-template")
        subject = request.POST.get("subject")
        reply = request.POST.get("reply")
        print(group, mail_template, subject, reply)
        group_mail(group, mail_template, subject, reply, seizoen)
        messages.success(request, """
        Mails succesvol verstuurd.
        """)
        return redirect(reverse('management:mails'))


def fetch_mail(request):
    """
    Fetch a mail template given with template
    """
    template = request.GET.get("template")
    return render(request, template)
