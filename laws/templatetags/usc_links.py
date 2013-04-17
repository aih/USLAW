import re
from django import template
from django.utils.functional import allow_lazy
from django.template.defaultfilters import stringfilter
from utils.utils import usc_add_links

register = template.Library()

@register.filter
def usc_links(value):
  """ Replaces 26USC501(c)(3) with corresponding link """
  return usc_add_links(value)

usc_links = stringfilter(usc_links)
usc_links.is_save=True
