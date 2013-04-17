# -*- coding: utf-8 -*-
# Tags views

from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils import simplejson
from django.db.models import Max

from utils.utils import render_to
from users.models import *
from tags.models import *
from laws.forms import SearchForm

@render_to("tags/add_tag.html")
def add(request):
    if request.method == "POST":
        form = TaggedItemForm(request.POST)
        if form.is_valid():
            tags = form.cleaned_data['tag']
            content_type = ContentType.objects.get(pk=form.cleaned_data['content_type'])
            object_id = form.cleaned_data['object_id']
            for t in tags.split(","):
                tag, c = Tag.objects.get_or_create(name=t.lower())
                to, c = TaggedItem.objects.get_or_create(tag=tag, content_type=content_type, object_id=object_id)
            return HttpResponseRedirect(form.cleaned_data['next'])
        else:
            for r in form:
                print r, r.errors

    else:
        form = TaggedItemForm(initial={'content_type': 1})
    return locals()

def flag_as_outdated(request):
    user = get_user_object(request)
    error = "Unknown error"
    if request.method == "GET":
        form = OutdatedResourceForm(request.GET)
        if form.is_valid():
            content_type = ContentType.objects.get(pk=form.cleaned_data['content_type'])
            object_id = form.cleaned_data['object_id']
            outres,c = OutdatedResource.objects.get_or_create(user=user, content_type=content_type, object_id=object_id)
            results = {'success':'Flaged'}                        
            json = simplejson.dumps(results)
            return HttpResponse(json, mimetype='application/json')
        else:
            print form.errors
            error = "Form is invalid"

    results = {'success':error}                        
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')


def tag_item(tags, content_object):
    """
    Add tags to object
    """
    for t in tags.split(","):
        tag, c = Tag.objects.get_or_create(name=t)
        to = TaggedItem(tag=tag, content_object=content_object)
        to.save()

    return True

@render_to("tags/browse.html")
def view_tags(request, tag_id):
    user = get_user_object(request)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        pass
    searchform = SearchForm()
    object_type = ContentType.objects.get_for_model(Profile)
    tag = get_object_or_404(Tag, pk=tag_id)
    tags = TaggedItem.objects.filter(tag__pk = tag_id).exclude(content_type=object_type).order_by("-publication_date")

    try:
        page_id = int(request.GET.get('p', 1))        
    except ValueError:
        page_id = 1

    paginator = Paginator(tags, 20)
    try:
        page = paginator.page(page_id)
    except EmptyPage:
        paginator = None

    return locals()

def tags_suggestion(request):
    """Suggested tags """
    t = request.GET.get('term', " ")
    if "," in t:
        tags = t.split(',')
        last_tag = tags[-1].strip()
        p_tags = tags[:-1]           
    else:
        last_tag = t
        p_tags = []

    last_tag=last_tag.strip()
    new_tags_list = Tag.objects.filter(name__startswith=last_tag).order_by('-is_users_interest', 'name')[:20]
    results = []
    p_tags = ",".join(p_tags)
    print p_tags

    for tt in new_tags_list:
        if len(p_tags)>0:
            results.append({'id':tt.id,'label':tt.name, 'value':p_tags+','+tt.name+","})
        else:
            results.append({'id':tt.id,'label':tt.name, 'value':tt.name+", "})
           

    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')

@render_to("tags/cloud.html")
def tags_cloud(request):
    tags_size_steps = 20
    tags_max = Tag.objects.filter().aggregate(Max('count'))
    fraction = int(tags_max / tags_size_steps)
    tags = Tag.objects.filter(count__gt=0)
    return locals()
