# -*- coding: utf-8 -*-
# Uslaw HELP views
# We have only one view - which uses the URL to define which help text to show.

from django.http import HttpResponse
from django.utils import simplejson as sjson
from django.db.models import Q

from users.models import Option, get_user_object

from help.models import *

def get_help(request):
    user = get_user_object(request)
    if user:
        try:
            options = Option.objects.get(user=user, name='display_help_bubbles')
        except Option.DoesNotExist:
            pass
        else:
            if options.bvalue == False:
                res = {"text": False }
                json = sjson.dumps(res)
                return HttpResponse(json, mimetype='application/json')
                
    url = request.GET.get('url', False)
    if url:
        res = {}
        h = Help.objects.filter(Q(url=url)|Q(default_help=True))
        if len(h) < 2:
            new_url = "/".join(url.split('/')[:-2])+"/"
            h = Help.objects.filter(Q(url=new_url)|Q(default_help=True))
        if len(h) > 0:
            one_time_notice_ = False
            for hh in h:
                if not one_time_notice_ and hh.one_time_notice and user: # We show only one "one time notice" per page view
                    sh, c = ShownHelp.objects.get_or_create(user=user,
                                                            notice=hh)
                    if c:
                        one_time_notice_ = True 
                        res[hh.widget_id] = hh.text

                elif not hh.one_time_notice and not hh.default_help:
                    res[hh.widget_id] = hh.text
            for hh in h:
                if hh.default_help:
                    if not res.get(hh.widget_id, False):
                        res[hh.widget_id] = hh.text
        else:
            res = {"text": False }
        json = sjson.dumps(res)
        return HttpResponse(json, mimetype='application/json')
    else:
        res = {"text": False }
        json = sjson.dumps(res)
        return HttpResponse(json, mimetype='application/json')
