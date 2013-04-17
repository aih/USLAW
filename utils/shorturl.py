# -*- coding: utf-8 -*-
# module for shorten urls with bit.ly

from django.conf import settings

import bitly

def bitly_short(url):
    """Short url with bit.ly """
    api = bitly.Api(login=settings.BITLY_LOGIN, apikey=settings.BITLY_KEY) 
    attempts, res = 2, False
    while not res and attempts > 0:
        attempts -= 1
        try:
            res = api.shorten(url, {'history':1})
        except TypeError:
            print "Bitly fails. Url: %s " % url
    return res
