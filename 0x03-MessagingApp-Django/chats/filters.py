import django_filters
from .models import User, Message

class MessageFilter(django_filters.FilterSet):
    sender = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    recipient = django_filters.ModelChoiceFilter(field_name='conversation__participants', queryset=User.objects.all())
    start_date = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Message
        fields = ['sender', 'recipient', 'start_date', 'end_date']
