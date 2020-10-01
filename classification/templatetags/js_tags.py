import urllib
from decimal import Decimal
from html import escape
from typing import Union

from django import template
from django.utils.safestring import mark_safe
import json

# FIXME, move this out of classifications and into snpdb
from classification.views.classification_datatables import DatatableConfig

register = template.Library()


@register.filter
def jsonify(json_me) -> Union[str, float]:
    if isinstance(json_me, str):
        return json_me
    elif isinstance(json_me, bool):
        if json_me:
            return mark_safe('true')
        else:
            return mark_safe('false')
    elif isinstance(json_me, int) or isinstance(json_me, float):
        return json_me
    text = json.dumps(json_me)
    text = text.replace('</script>','<\\/script>')
    return mark_safe(text)


@register.filter
def query_unquote(query_string):
    return urllib.parse.unquote(query_string)


@register.filter
def jsstring(text):
    if text:
        text = text.replace('\\', '\\\\').replace('`','\`').replace('</script>','<\\/script>')
        return mark_safe(text)
    else:
        return ''


@register.filter
def limit_length(text, limit=100):
    if text and len(text) > limit:
        return text[0:(limit-3)] + '...'
    return text


@register.filter(is_safe=True)
def format_value(val):
    if val is None:
        return mark_safe('<span class="none">None</span>')
    if val == "":
        return mark_safe('<span class="none">""</span>')
    if isinstance(val, dict) or isinstance(val, list):
        return mark_safe(f'<span class="json">{escape(json.dumps(val))}</span>')
    if isinstance(val, float):
        val = format(Decimal(str(val)).normalize(), 'f')
    else:
        val = str(val)
    return mark_safe(f'<span>{escape(val)}</span>')


@register.filter()
def format_computer_text(val):
    if val is None:
        return ''
    return val.replace('&', ' & ').replace('_', ' ')


@register.filter()
def dash_if_empty(val):
    if val is None or len(val.strip()) == 0:
        return mark_safe('<span class="no-value">-</span>')
    return val


@register.inclusion_tag("classification/tags/timestamp.html")
def timestamp(timestamp, time_ago: bool = False):
    css_class = 'time-ago' if time_ago else ''
    if timestamp:
        if not isinstance(timestamp, int):
            timestamp = timestamp.timestamp()
        return {
            "timestamp": timestamp,
            "css_class": css_class
        }
    else:
        return {"css_class": "empty"}


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def format_preference(value):
    if value == True:
        return 'Yes'
    elif value == False:
        return 'No'
    else:
        return value


@register.filter
def times(value):
    return range(0, value)