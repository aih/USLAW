# -*- coding: utf-8 -*-
# Misc utils for Tax26.com Project

import logging
import re

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import Http404
from django.conf import settings #LOG_FILE, DEBUG

def usc_repl(matchobj):

    if len(matchobj.groups()) == 2:
        new_value = u" <a class='usc_link' href='/laws/%s/%s/'>%s USC § %s</a> " % (matchobj.group(1), matchobj.group(2), matchobj.group(1), matchobj.group(2))
    elif len(matchobj.groups()) == 3:
        new_value = u" <a class='usc_link' href='/laws/%s/%s/'>%s USC § %s%s</a> " % (matchobj.group(1), matchobj.group(2), matchobj.group(1), matchobj.group(2), matchobj.group(3))
    else:
        return matchobj.group(0)
    return new_value

def usc_add_links(value):
    usc_re = re.compile(r'\[(\d+)\s?U\.?S\.?C\.?\s?(\d+)(.*?)\]', re.IGNORECASE)
    new_value = usc_re.sub(usc_repl, value)
    return new_value

def getlogger():
    logger = logging.getLogger()
    hdlr = logging.FileHandler(settings.LOG_FILE)
    formatter = logging.Formatter('[%(asctime)s]%(levelname)-8s"%(message)s"','%Y-%m-%d %a %H:%M:%S') 
    
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)

    return logger

def debug(msg):
    if settings.DEBUG:
        logger = getlogger()
        logger.debug(msg)

def render_to(template):
    """
    Decorator for Django views that sends returned dict to render_to_response function
    with given template and RequestContext as context instance.

    If view doesn't return dict then decorator simply returns output.
    Additionally view can return two-tuple, which must contain dict as first
    element and string with template name as second. This string will
    override template name, given as parameter

    Parameters:

    — template: template name to use
    """
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if isinstance(output, (list, tuple)):
                return render_to_response(output[1], output[0], RequestContext(request))
            elif isinstance(output, dict):
                return render_to_response(template, output, RequestContext(request))
            return output
        return wrapper
    return renderer


from django.db import connection
from django.template import Template, Context

class SQLLogMiddleware:

    def process_response ( self, request, response ): 
        time = 0.0
        for q in connection.queries:
		time += float(q['time'])
        
        t = Template('''
            <p><em>Total query count:</em> {{ count }}<br/>
            <em>Total execution time:</em> {{ time }}</p>
            <ul class="sqllog">
                {% for sql in sqllog %}
                    <li>{{ sql.time }}: {{ sql.sql }}</li>
                {% endfor %}
            </ul>
        ''')


        content = response.content.decode('utf-8')
        content += t.render(Context({ 
                    'sqllog':connection.queries,
                    'count':len(connection.queries),'time':time}))
        response.content = content.encode('utf-8')
        return response
#        response.content = "%s%s" % ( response.content, t.render(Context({'sqllog':connection.queries,'count':len(connection.queries),'time':time})))
 #       return response



def humanizeTimeDiff(timestamp = None):
    """
    Returns a humanized string representing time difference
    between now() and the input timestamp.
    
    The output rounds up to days, hours, minutes, or seconds.
    4 days 5 hours returns '4 days'
    0 days 4 hours 3 minutes returns '4 hours', etc...

    from http://djangosnippets.org/snippets/412/
    """
    import datetime
    
    timeDiff = datetime.datetime.now() - timestamp
    days = timeDiff.days
    hours = timeDiff.seconds/3600
    minutes = timeDiff.seconds%3600/60
    seconds = timeDiff.seconds%3600%60
    
    str = ""
    tStr = ""
    if days > 0:
        if days == 1:   tStr = "day ago"
        else:           tStr = "days ago"
        str = str + "%s %s" %(days, tStr)
        return str
    elif hours > 0:
        if hours == 1:  tStr = "hour ago"
        else:           tStr = "hours ago" 
        str = str + "%s %s" %(hours, tStr)
        return str
    elif minutes > 0:
        if minutes == 1:tStr = "min ago"
        else:           tStr = "mins ago"           
        str = str + "%s %s" %(minutes, tStr)
        return str
    elif seconds > 0:
        if seconds == 1:tStr = "sec ago"
        else:           tStr = "secs ago"
        str = str + "%s %s" %(seconds, tStr)
        return str
    else:
        return None

def get_page_range(paginator, page):
    """
    Generate page range
    """
    _PAGE_LINKS = 15
    page_range = []
    if 4 > page:
        if len(paginator.page_range)>_PAGE_LINKS:
            page_range = [p for p in range(1, _PAGE_LINKS+1)]
        else:
            page_range = paginator.page_range
    else:
        for p in paginator.page_range:
            if p < page:
                if page-p < (_PAGE_LINKS)//2:
                    page_range.append(p)
            if p>=page:
                if p-page < (_PAGE_LINKS)//2:
                    page_range.append(p)

        if len(page_range) > _PAGE_LINKS and page > (_PAGE_LINKS)//2:
            page_range = page_range[:-1] 
    return page_range

def prepeare_pagination(parts, request):
    """Prepeare page range"""
    paginator = Paginator(parts, 30)
    try:
        page_id = int(request.GET.get('p', 1))
    except ValueError:
        page_id = 1
    try:
        page = paginator.page(page_id)
    except EmptyPage, InvalidPage:
        raise Http404
    page_range = get_page_range(paginator, page_id)
    return paginator, page, page_range, page_id
