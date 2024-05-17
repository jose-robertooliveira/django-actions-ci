from typing import Any
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.db.models import QuerySet
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import Question, Choice


class IndexView(generic.ListView):
    template_name = "pools/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self) -> QuerySet[Question]:
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("pub_date")[:5]

def index(request):
    latest_question_list: QuerySet[Question] = Question.objects.order_by("-pub_date")[:5]
    
    context = {
        'latest_question_list': latest_question_list}
    return render(request, 'pools/index.html', context)

class DetailView(generic.DetailView):
    model = Question
    template_name = "pools/detail.html"

    def get_queryset(self) -> QuerySet[Question]:
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "pools/results.html"

def detail(request: HttpRequest, question_id: int) -> HttpResponse:
    question = get_object_or_404(Question, id=question_id)
    return render(request, "pools/detail.html", {"question": question})
    
def results(request: HttpRequest, question_id: int) -> HttpResponse:
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "pools/results.html", {"question": question})

def vote(request: HttpRequest, question_id: int) -> HttpResponse:
    question: Question =  get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'pools/detail.html', {
            'question': question,
            'error_message': "You did not select a choice"
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('pools:results', args=(question_id, )))

