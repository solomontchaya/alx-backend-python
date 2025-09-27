import django_filters
from .models import Message

class MessageFilter(django_filters.FilterSet):
    user = django_filters.NumberFilter(
        field_name='conversation__participants__id',
        lookup_expr='exact',
        label='Participant ID'
    )
    sent_after = django_filters.DateTimeFilter(
        field_name='sent_at', lookup_expr='gte', label='Sent After'
    )
    sent_before = django_filters.DateTimeFilter(
        field_name='sent_at', lookup_expr='lte', label='Sent Before'
    )

    class Meta:
        model = Message
        fields = ['user', 'sent_after', 'sent_before']
