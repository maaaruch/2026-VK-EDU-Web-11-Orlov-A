from django.contrib import admin
from django.db import models
from django.forms import Textarea
from .models import Question, Answer, Tag, QuestionLike, AnswerLike


class AnswerInline(admin.TabularInline):
    model = Answer
    fields = ('author', 'text', 'is_correct', 'rating')
    raw_id_fields = ('author',)
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'rating', 'created_at')
    search_fields = ('title', 'text', 'author__username')
    list_filter = ('created_at',)
    list_select_related = ('author',)
    raw_id_fields = ('author', 'tags')
    inlines = [AnswerInline]
    formfield_overrides = {models.CharField: {'widget': Textarea(attrs={'rows': 2, 'cols': 60})}}


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'author', 'is_correct', 'rating', 'created_at')
    search_fields = ('text', 'author__username', 'question__title')
    list_filter = ('is_correct', 'created_at')
    list_select_related = ('author', 'question')
    raw_id_fields = ('author', 'question')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    list_filter = (('name', admin.EmptyFieldListFilter),)


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'question', 'value')
    search_fields = ('user__username', 'question__title')
    list_filter = ('value',)
    list_select_related = ('user', 'question')
    raw_id_fields = ('user', 'question')


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'answer', 'value')
    search_fields = ('user__username', 'answer__text')
    list_filter = ('value',)
    list_select_related = ('user', 'answer')
    raw_id_fields = ('user', 'answer')
