from django.shortcuts import render, redirect, reverse
from django.views import generic
from django.views.generic.edit import FormView, UpdateView

from .models import Lid, Functie, Ouder
from .forms import LidForm


class IndexView(generic.TemplateView):
    template_name = "management/index.html"


class LidListView(generic.ListView):
    model = Lid
    template_name = "management/lid_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header"] = Lid.HEADER_NAMEN
        context["fields"] = Lid.FIELD_NAMEN
        return context


class LidNewView(FormView):
    template_name = 'management/lid_edit.html'
    form_class = LidForm
    succes_url = 'management:leden'

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("management:leden")


class LidEditView(UpdateView):
    template_name = 'management/lid_edit.html'
    template_name_suffix = ""
    form_class = LidForm
    model = Lid

    def get_success_url(self):
        return reverse("management:leden")

