from django.shortcuts import render, redirect
from .models import Suggestions
from .forms import SuggestionsForm
from django.views.generic import DetailView


def suggestions_home(request):
    suggestions = Suggestions.objects.order_by('date')
    return render(request, 'suggestions/suggestions_home.html', {'suggestions': suggestions})


class SuggestionsDetailView(DetailView):
    model = Suggestions
    template_name = 'suggestions/full_open.html'
    context_object_name = 'suggestion'


def create(request):
    error = ''
    if request.method == 'POST':
        form = SuggestionsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            error = 'Форма была неверной'

    form = SuggestionsForm()

    data = {
        'form': form,
        'error': error
    }

    return render(request, 'suggestions/create.html', data)