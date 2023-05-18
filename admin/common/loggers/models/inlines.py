from django.contrib.admin import StackedInline


class BaseLogInline(StackedInline):
    readonly_fields = (
        'created',
        'state_before',
        'state_after',
        'state_difference',
        'content',
        'error_data',
        'response_data',
        'use_case'
    )
    extra = 0
    classes = ['collapse']
