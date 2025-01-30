import logging

from random import shuffle
from datetime import datetime, timedelta

from verbalvoyager.settings import DEBUG_LOGGING_FP
from django import template

register = template.Library()


@register.filter(name="sentences_split", is_safe=True)
def sentences_split(values):
    return values.split('\r\n')

@register.filter(name="get_shuffled_translates", is_safe=True)
def get_shuffled_translates(values):
    translates = [{'idx': idx + 1, 'translate': word['translate']} for idx, word in enumerate(values)]
    shuffle(translates)
    return translates
