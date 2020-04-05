from django.shortcuts import render
from django.views import generic

from .models import Lid, Functie, Ouder

class IndexView(generic.TemplateView):
    template_name = "management/index.html"

class LidListView(generic.ListView):
    model = Lid

class LidDetailView(generic.DetailView):
    model = Lid

