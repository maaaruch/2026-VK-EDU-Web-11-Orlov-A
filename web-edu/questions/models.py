from django.conf import settings
from django.db import models
from django.urls import reverse
from core.models import DefaultModel
from .managers import QuestionManager, AnswerManager


class Tag(models.Model):
    name = models.CharField('Название тега', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Question(DefaultModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='questions', verbose_name='Автор вопроса')
    title = models.CharField('Заголовок вопроса', max_length=150)
    text = models.CharField('Текст вопроса', max_length=4095)
    tags = models.ManyToManyField(Tag, related_name='questions', blank=True,
                                 verbose_name='Теги вопроса')
    rating = models.IntegerField('Рейтинг вопроса', default=0)
    objects = QuestionManager()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        indexes = [
            models.Index(fields=['-created_at', '-id'], name='question_newest_idx'),
            models.Index(fields=['-rating', '-id'], name='question_rating_idx'),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('questions:question', args=[self.pk])


class Answer(DefaultModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='answers', verbose_name='Автор ответа')
    question = models.ForeignKey(Question, on_delete=models.CASCADE,
                                 related_name='answers', verbose_name='Вопрос')
    text = models.CharField('Текст ответа', max_length=4095)
    is_correct = models.BooleanField('Правильный ответ', default=False)
    rating = models.IntegerField('Рейтинг ответа', default=0)
    objects = AnswerManager()

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        indexes = [models.Index(fields=['question', '-rating', '-created_at', '-id'],
                                name='answer_question_rating_idx')]

    def __str__(self):
        return self.text[:50]


class QuestionLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='question_likes', verbose_name='Пользователь')
    question = models.ForeignKey(Question, on_delete=models.CASCADE,
                                 related_name='likes', verbose_name='Вопрос')
    value = models.SmallIntegerField('Оценка', choices=[(1, 'Лайк'), (-1, 'Дизлайк')])

    class Meta:
        verbose_name = 'Оценка вопроса'
        verbose_name_plural = 'Оценки вопросов'
        constraints = [
            models.UniqueConstraint(fields=['user', 'question'], name='user_question_unique'),
            models.CheckConstraint(condition=models.Q(value__in=[-1, 1]), name='question_like_value_valid'),
        ]

    def __str__(self):
        return f'Пользователь {self.user_id}, вопрос {self.question_id}: {self.value}'


class AnswerLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='answer_likes', verbose_name='Пользователь')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE,
                               related_name='likes', verbose_name='Ответ')
    value = models.SmallIntegerField('Оценка', choices=[(1, 'Лайк'), (-1, 'Дизлайк')])

    class Meta:
        verbose_name = 'Оценка ответа'
        verbose_name_plural = 'Оценки ответов'
        constraints = [
            models.UniqueConstraint(fields=['user', 'answer'], name='user_answer_unique'),
            models.CheckConstraint(condition=models.Q(value__in=[-1, 1]), name='answer_like_value_valid'),
        ]

    def __str__(self):
        return f'Пользователь {self.user_id}, ответ {self.answer_id}: {self.value}'
