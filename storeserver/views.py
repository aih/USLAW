# -*- coding: utf-8 -*-
#
import re
from urlparse import urlparse, urljoin
from datetime import timedelta,datetime
from random import randint

from django.template import loader, Context
from django.http import HttpResponse
from django.db.models import Q
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from storeserver.models import Store, Link
from plugins.models import Plugin
from local_bot_settings import SECRET_KEY as skey
from local_settings import DEBUG


def index(request):
    """
    Small index/'hello world' page
    """
    c = Store.objects.count()
    html = "<h1>Hello world!</h1> I have "+str(c)+" pages loaded in me."
    return HttpResponse(html)

@csrf_exempt
@never_cache
def save(request):
    """
    Interface for saving pages into Store-server
    """
    if request.method == 'POST':
        p = request.POST
        secret_key = p['secret_key']
        if secret_key != skey and DEBUG == False:  # Ok, somebody with wrong secret key.
            raise Exception, "Internal server error"
        
        url = p['url']
        page = p['page']
        plugin_id=p['plugin_id']
        plugin_level = p['plugin_level']
        page_type= p['page_type']
        status=p['status']
        error_text = p['error']

        s = Store(url=url, page=unicode(page), status=status, plugin_id=plugin_id, plugin_level=plugin_level, page_type=page_type, error_text=error_text)
        s.save()            
        res = "Ok"
    else:
        res = "What are you  doing here?"
    return HttpResponse(res, mimetype="text/plain")


@never_cache
def get_urls(request, url_type, secret_key):
    """
    Return list of links to download

    url_type - Type of url, 0 - text/html, 1 - image/file
    s_key - Secret key to acces database.
    return a list of links separated with |
    Example: site1.com|site2.com|site3.com
    
    """

    if secret_key.replace('/','') != skey and DEBUG == False:  # Ok, somebody with wrong secret key.
        raise Exception, "Internal server error"

    urls = []
    for pl in Plugin.objects.filter(status=1):
        u = Link.objects.filter(url_type=url_type, status=0, plugin_id=pl.plugin_id).order_by("?")[:1]
        if len(u) > 0:
            urls.append(u[0])

    links = ""
    if len(urls) == 0:
        links = "No urls"
    else:
        for u in urls:
            skip = False
            now = datetime.now()
            plugin = Plugin.objects.get(plugin_id=u.plugin_id)
            if plugin.download_rate and plugin.download_rate != "":
                last_url = Link.objects.filter(plugin_id=u.plugin_id, status=1).order_by("-publication_date")[:1]
                if last_url:
                    d = timedelta(seconds=plugin.download_rate)
                    if now - last_url[0].date_taken < d:
                        skip = True

            if skip == False:
                links = links+"|||"+u.url+"%%%"+str(u.plugin_id)+"%%%"+str(u.plugin_level)+"%%%"+ u.decode_charset + "%%%" + str(u.category_id)+"|||" 
                u.date, u.date_taken = now, now
                u.status=1
                u.save()
                #print u.date, u.date_taken
    resp = HttpResponse(links, mimetype="text/plain")
    return resp

@never_cache
def stat(request):
    """
    Display some statistics
    """
    
    return locals()
