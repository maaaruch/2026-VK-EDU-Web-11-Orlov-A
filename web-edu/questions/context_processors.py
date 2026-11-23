from django.contrib.auth import get_user_model
from django.db.models import Count
from .models import Tag


def sidebar(request):
    return {
        'sidebar_tags': Tag.objects.annotate(total=Count('questions')).order_by('-total', 'id')[:8],
        'sidebar_members': get_user_model().objects.annotate(total=Count('questions')).order_by('-total', 'id')[:3],
    }
