from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.test.utils import override_settings
from faker import Faker

from core.models import Profile
from questions.models import Question, Answer, Tag, QuestionLike, AnswerLike


class Command(BaseCommand):
    help = 'Добавить тестовые данные: ratio пользователей, 10× вопросов, 100× ответов, 200× голосов.'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def insert_batches(self, model, objects, batch_size):
        batch = []
        for obj in objects:
            batch.append(obj)
            if len(batch) >= batch_size:
                model.objects.bulk_create(batch, batch_size=batch_size)
                batch.clear()
        if batch:
            model.objects.bulk_create(batch, batch_size=batch_size)
            batch.clear()

    def handle(self, *args, **options):
        ratio = options['ratio']
        batch_size = 5000
        if ratio < 2:
            raise CommandError('ratio должен быть >= 2. При ratio=1 недостаточно уникальных пар для 200 голосов.')
        
        with override_settings(DEBUG=False), transaction.atomic():
            self.fill(ratio, batch_size)

    def fill(self, ratio, batch_size):
        fake = Faker('ru_RU')
        prefix = uuid4().hex[:12]
        User = get_user_model()
        self.insert_batches(User, (
            User(username=f'{prefix}_{i}', first_name=fake.first_name(),
                 last_name=fake.last_name(), email=f'{prefix}_{i}@example.com',
                 password='!')
            for i in range(ratio)
        ), batch_size)
        users = list(User.objects.filter(username__startswith=prefix + '_').order_by('id').values_list('id', flat=True))
        self.insert_batches(Profile, (Profile(user_id=pk) for pk in users), batch_size)
        self.insert_batches(Tag, (
            Tag(name=f'{fake.word()[:25]}-{prefix}-{i}') for i in range(ratio)
        ), batch_size)
        tags = list(Tag.objects.filter(name__contains='-' + prefix + '-').order_by('id').values_list('id', flat=True))
        self.stdout.write(f'Пользователей и тегов: по {ratio}')

        question_votes = min(ratio, 10)
        values = [1 if i % 4 else -1 for i in range(question_votes)]
        question_ids = []
        batch = []
        for i in range(ratio * 10):
            batch.append(Question(author_id=users[i % ratio], title=fake.sentence()[:150],
                                  text=fake.paragraph(nb_sentences=5)[:4095], rating=sum(values)))
            if len(batch) >= batch_size:
                self.save_questions(batch, users, tags, values, question_ids, batch_size)
                batch.clear()
        if batch:
            self.save_questions(batch, users, tags, values, question_ids, batch_size)
            batch.clear()
        self.stdout.write(f'Вопросов: {len(question_ids)}')

        answer_count = ratio * 100
        remaining_votes = ratio * 200 - len(question_ids) * question_votes
        votes_per_answer, extra_votes = divmod(remaining_votes, answer_count)
        batch = []
        batch_counts = []
        for i in range(answer_count):
            count = votes_per_answer + (i < extra_votes)
            rating = sum(1 if j % 4 else -1 for j in range(count))
            batch.append(Answer(author_id=users[i % ratio],
                                question_id=question_ids[i // 10],
                                text=fake.paragraph(nb_sentences=3)[:4095],
                                is_correct=i % 10 == 0, rating=rating))
            batch_counts.append(count)
            if len(batch) >= batch_size:
                self.save_answers(batch, batch_counts, users, batch_size)
                batch.clear()
                batch_counts.clear()
        if batch:
            self.save_answers(batch, batch_counts, users, batch_size)
            batch.clear()
            batch_counts.clear()
        self.stdout.write(self.style.SUCCESS(
            f'Добавлено: {ratio} пользователей, {ratio} тегов, {ratio * 10} вопросов, '
            f'{answer_count} ответов, {ratio * 200} голосов.'))

    def save_questions(self, batch, users, tags, values, question_ids, batch_size):
        Question.objects.bulk_create(batch, batch_size=batch_size)
        through = Question.tags.through
        self.insert_batches(through, (
            through(question_id=q.pk, tag_id=tags[(q.pk + j) % len(tags)])
            for q in batch for j in range(min(3, len(tags)))
        ), batch_size)
        self.insert_batches(QuestionLike, (
            QuestionLike(question_id=q.pk, user_id=users[(q.pk + j) % len(users)], value=value)
            for q in batch for j, value in enumerate(values)
        ), batch_size)
        question_ids.extend(q.pk for q in batch)

    def save_answers(self, batch, counts, users, batch_size):
        Answer.objects.bulk_create(batch, batch_size=batch_size)
        self.insert_batches(AnswerLike, (
            AnswerLike(answer_id=a.pk, user_id=users[(a.pk + j) % len(users)],
                       value=1 if j % 4 else -1)
            for a, count in zip(batch, counts) for j in range(count)
        ), batch_size)
