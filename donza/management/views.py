from django.contrib import messages
from django.shortcuts import redirect, render, reverse
from django.views import generic
from django.views.generic.edit import FormView, UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin

from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from .visual.forms import LidForm, OuderForm, PloegForm
from .models import Lid, Ploeg, PloegLid
from .visual.tables import LidTable
from .visual.filters import LidFilter
from .main.ledenbeheer import import_from_csv
# Deze lijn moet er in blijven staan om de TeamSelector te kunnen laden


class IndexView(generic.TemplateView):
    template_name = "management/index.html"


class LidListView(generic.ListView):
    model = Lid
    template_name = "management/lid_list.html"
    paginate_by = 20

    def post(self, request, *args, **kwargs):
        # retrieve the file from the request
        csv_file = request.FILES['file']

        # retrieve information for rendering
        template = "management/lid_list.html"
        if not csv_file.name.endswith(".csv"):
            messages.error(request, "This is not a csv file")

            # retrieve the object list to display
            self.object_list = self.model.objects.all()
            context = self.get_context_data(**kwargs)
            return render(request, template, context)

        import_from_csv(csv_file, request)

        # after importing the csv, refresh the object list
        self.object_list = self.model.objects.all()
        context = self.get_context_data(**kwargs)

        return render(request, template, context)


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
        leden_ids = [ploeglid.lid.club_id for ploeglid in PloegLid.objects.filter(
            ploeg_id=ploeg.ploeg_id)]
        return leden_ids


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
    permission_required = ('lid.can_view',)
    permission_denied_message = """
    Je hebt niet de juiste permissies om deze pagina te bekijken. 
    Indien je dit wel nodig hebt, contacteer de webmaster. (TODO: add link)
    """

    def post(self, request, *args, **kwargs):
        # retrieve the file from the request
        csv_file = request.FILES['file']

        # retrieve information for rendering
        template = "management/lid_list.html"
        if not csv_file.name.endswith(".csv"):
            messages.error(request, "This is not a csv file")

            # retrieve the object list to display
            self.object_list = self.model.objects.all()
            context = self.get_context_data(**kwargs)
            return render(request, template, context)

        import_from_csv(csv_file, request)

        # after importing the csv, refresh the object list
        self.object_list = self.model.objects.all()
        context = self.get_context_data(**kwargs)

        return render(request, template, context)


def genereer(request):
    if request.method == "POST":
        pks = request.POST.getlist("selection")
        selected_objects = Lid.objects.filter(pk__in=pks)
        # do something with selected_objects


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
