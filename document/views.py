# -*- coding: utf-8 -*-
# Document views

from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator,InvalidPage, EmptyPage
from django.core import serializers
from django.utils import simplejson

from utils.utils import render_to
from users.models import get_user_object, get_profile_object
from document.models import Document

@render_to("document/list.html")
def document_list(request):
    """Get document list for profile """
    results = {'success':False}
    user = get_user_object(request)
    profile = get_profile_object(user)
    documents = Document.objects.filter(profile=profile)
    return locals()

@render_to("document/save.html")
def document_save(request):
    """Save document for profile """
    results = {'success':False}
    user = get_user_object(request)
    profile = get_profile_object(user)
    if profile:
        content_type = ContentType.objects.get(pk=request.GET['content_type_id'])
        s = Document.objects.filter(profile=profile, object_id=request.GET['object_id'], content_type = content_type).count()
        if s==0:
            s = Document(profile=profile, object_id=request.GET['object_id'], content_type = content_type)
            s.save()
        else:
            s = False
    else:
        s = None
    return locals()

def document_delete(request):
    """Delete document  for profile """
    results = {'success':'Deleted'}
    try:
        user = get_user_object(request)
        profile = get_profile_object(user)
        d = Document.objects.filter(profile=profile, pk=request.GET['document_id']).delete()# content_type__pk = request.GET['content_type_id'], object_id = request.GET['object_id']).delete()
    except:
        results = {'success':'Error'}
    
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')


