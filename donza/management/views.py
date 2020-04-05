from django.shortcuts import render, redirect
from django.views import generic

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

class LidDetailView(generic.DetailView):
    model = Lid

def post_new(request):
    if request.method == "POST":
        form = LidForm(request.POST)
        if form.is_valid():
            lid = form.save(commit=False)
            lid.save()
            return redirect('management:leden')
    else:
        form = LidForm()
    return render(request, 'management/lid_edit.html', {'form': form})

