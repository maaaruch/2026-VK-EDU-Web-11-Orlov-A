from django.shortcuts import get_object_or_404, render
from .models import Question, Answer, Tag
from .pagination import paginate


def question_list(request, queryset, template, **context):
    page_obj = paginate(queryset, request)
    return render(request, template, {
        'questions': page_obj.object_list, 'page_obj': page_obj, **context,
    })


def index(request):
    return question_list(request, Question.objects.newest(), 'questions/index.html')


def hot(request):
    return question_list(request, Question.objects.popular(), 'questions/hot.html')


def tag(request, tag):
    tag = get_object_or_404(Tag, name=tag)
    return question_list(request, Question.objects.by_tag(tag), 'questions/tag.html', tag=tag)


def question(request, question_id):
    question = get_object_or_404(Question.objects.for_display(), pk=question_id)
    page_obj = paginate(Answer.objects.for_question(question), request)
    return render(request, 'questions/question.html', {
        'question': question, 'answers': page_obj.object_list, 'page_obj': page_obj,
    })


def ask(request):
    return render(request, 'questions/ask.html')
