from django.db import models
from django.db.models import Count, OuterRef, Subquery
from django.db.models.functions import Coalesce


class QuestionManager(models.Manager):
    def for_display(self):
        from .models import Answer
        counts = Answer.objects.filter(question_id=OuterRef('pk')).order_by().values('question_id').annotate(total=Count('id')).values('total')
        return self.select_related('author', 'author__profile').prefetch_related('tags').annotate(
            answer_count=Coalesce(Subquery(counts), 0))

    def newest(self):
        return self.for_display().order_by('-created_at', '-id')

    def popular(self):
        return self.for_display().order_by('-rating', '-id')

    def by_tag(self, tag):
        return self.popular().filter(tags=tag)


class AnswerManager(models.Manager):
    def for_question(self, question):
        return self.select_related('author', 'author__profile').filter(
            question=question).order_by('-rating', '-created_at', '-id')
