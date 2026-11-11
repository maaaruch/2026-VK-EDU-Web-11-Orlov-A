from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404
from django.shortcuts import render


QUESTIONS_LIST = [
    {
        'id': i,
        'title': f'Вопрос {i}',
        'text': f'Текст вопроса {i}. ' * 10,
        'rating': i,
        'tags': ['html', 'css'] if i % 2 == 0 else ['python'],
        'answer_count': 12,
    } for i in range(1, 31)
]


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    try:
        page = paginator.page(request.GET.get('page', 1))
    except (PageNotAnInteger, EmptyPage):
        page = paginator.page(1)
    return page


def index(request):
    page_obj = paginate(QUESTIONS_LIST, request, 5)
    return render(request, 'questions/index.html', {
        'questions': page_obj.object_list, 'page_obj': page_obj,
    })


def hot(request):
    page_obj = paginate(QUESTIONS_LIST[::-1], request, 5)
    return render(request, 'questions/hot.html', {
        'questions': page_obj.object_list, 'page_obj': page_obj,
    })


def tag(request, tag):
    questions = [question for question in QUESTIONS_LIST if tag in question['tags']]
    page_obj = paginate(questions, request, 5)
    return render(request, 'questions/tag.html', {
        'questions': page_obj.object_list, 'page_obj': page_obj, 'tag': tag,
    })


def question(request, question_id):
    question = None
    for item in QUESTIONS_LIST:
        if item['id'] == question_id:
            question = item
            break
    if question is None:
        raise Http404('Вопрос не найден')
    answers = [
        {'text': f'Ответ {i} на вопрос {question_id}.', 'rating': 13 - i, 'correct': i == 1}
        for i in range(1, 13)
    ]
    page_obj = paginate(answers, request, 5)
    return render(request, 'questions/question.html', {
        'question': question, 'answers': page_obj.object_list, 'page_obj': page_obj,
    })


def ask(request):
    return render(request, 'questions/ask.html')
