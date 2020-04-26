import csv
import datetime
import io
import re

from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.shortcuts import redirect, render, reverse
from django.views import generic
from django.views.generic.edit import FormView, UpdateView

from .components import TeamSelector
from .forms import LidForm, OuderForm
from .models import Functie, Lid, Ouder, Ploeg, PloegLid

GSM_PATTERN = "\d{4}\\\d{4}"
ADRES_PATTERN = r"(\d+)(.*)"


class IndexView(generic.TemplateView):
    template_name = "management/index.html"


class LidListView(generic.ListView):
    model = Lid
    template_name = "management/lid_list.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        csv_file = request.FILES['file']
        if not csv_file.name.endswith(".csv"):
            messages.error(request, "This is not a csv file")
        # TODO: put this in a separate function

        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)

        next(io_string)
        for index, row in enumerate(csv.reader(io_string, delimiter=';', quotechar="|")):
            geboortedatum = datetime.datetime.strptime(
                row[6], '%d/%m/%Y').strftime('%Y-%m-%d') if row[6] else None
            gescheiden = True if row[13] else False
            gsmnummer = row[7] if bool(re.match(GSM_PATTERN, row[7])) else None
            straatnaam = " ".join(row[3].split()[:-1])
            adres_match = re.match(ADRES_PATTERN, row[3].split()[-1])
            huisnummer = adres_match[1]
            bus = adres_match[2] if adres_match else ""
            _, created = Lid.objects.update_or_create(
                voornaam=row[0],
                familienaam=row[1],
                straatnaam=straatnaam,
                huisnummer=huisnummer,
                bus=bus,
                postcode=row[4],
                gemeente=row[5],
                geboortedatum=geboortedatum,
                gsmnummer=row[7],
                email=row[10],
                gescheiden_ouders=gescheiden,
                extra_informatie=row[14],
                rekeningnummer=row[15],
                betalend_lid=True,
                moeder_id=Ouder.objects.get(pk=1),
                vader_id=Ouder.objects.get(pk=2),
                lidnummer_vbl=index,
            )
        template = "management/lid_list.html"
        self.object_list = self.model.objects.all()
        context = self.get_context_data(**kwargs)
        return render(request, template, context)


class LidNewView(FormView):
    template_name = 'management/lid_edit.html'
    form_class = LidForm

    def form_valid(self, form):
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

    def get_success_url(self):
        return reverse("management:leden")


class PloegListView(generic.ListView):
    model = Ploeg
    template_name = "management/ploeg_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PloegSelectView(generic.DetailView):
    model = Ploeg
    template_name = 'management/ploeg_select.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ploeg = context['object']
        context['eligible_players'] = self.get_eligible_players(ploeg)
        context['ploegleden'] = self.get_ploegleden(ploeg)
        context['ploeg_id'] = ploeg.ploeg_id
        return context

    @staticmethod
    def get_eligible_players(ploeg):
        max_jaar = datetime.date.today().year-ploeg.leeftijdscategorie
        queryset = Lid.objects.all().filter(sportief_lid=True).exclude(
            geboortedatum=None).filter(geboortedatum__year__gte=max_jaar)
        ep = [lid.club_id for lid in queryset]
        return ep

    @staticmethod
    def get_ploegleden(ploeg):
        leden_ids = [ploeglid.lid_id.club_id for ploeglid in PloegLid.objects.filter(
            ploeg_id=ploeg.ploeg_id)]
        return leden_ids


def create_ouder(request):
    print(request.POST)
    ouder_form = OuderForm(request.POST)
    redirect_path = request.POST.get("next")
    if ouder_form.is_valid():
        ouder_form.save()
    else:
        messages.add_message(request, messages.ERROR,
                             "Ongeldig formulier voor nieuwe ouder")
    return redirect(redirect_path)
