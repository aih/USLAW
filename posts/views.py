# -*- coding: utf-8 -*-
# Posts views

from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator,InvalidPage, EmptyPage
from django.core import serializers
from django.utils import simplejson
from django.http import Http404

from utils.utils import render_to, prepeare_pagination
from tags.models import TaggedItem, Tag
from posts.models import *
from users.models import Profile, get_user_object, get_profile_object
from comment.models import Comment, CommentForm, FollowObject
from laws.forms import SearchForm

@render_to("posts/view.html")
def view(request, post_id):
    """Display news/questions with given news_id"""
    searchform = SearchForm()
    post = get_object_or_404(Post, pk=post_id)
    object_ = post
    content_type = ContentType.objects.get_for_model(Post)

    tags = TaggedItem.objects.filter(object_id=post.id, content_type__pk=content_type.id )
    tags_list = [t.tag.id for t in tags]
    related_objects = TaggedItem.objects.filter(content_type__pk=content_type.id, tag__pk__in= tags_list).order_by('-publication_date')[:50]
    related_objects_list = [r.object_id for r in related_objects]
    related_posts = Post.objects.filter(pk__in = related_objects_list, post_type=post.post_type).exclude(pk=post.pk).order_by('-publication_date').distinct()[:10]

    comment_form = CommentForm(initial={'content_type':content_type})
    comments = Comment.objects.filter(content_type=content_type, object_id=post.id).order_by("-rate")
    comments_count = Comment.objects.filter(content_type=content_type, object_id=post.id).count()
    user = get_user_object(request)
    profile = get_profile_object(user)
    follow_c = FollowObject.objects.filter(content_type=content_type, object_id = post_id, profile=profile).count()
    if follow_c > 0:
        follow = True
    else:
        follow = False

    cant_delete = False
    for c in comments:
        if c.profile != profile: # allow delete posts if there no comments from another users
            cant_delete = True
            break
        
    return locals()

@login_required()
@render_to("posts/delete.html")
def delete(request, post_id):
    """Deleting user post"""
    post = get_object_or_404(Post, pk=post_id)
    object_ = post
    content_type = ContentType.objects.get_for_model(Post)

    tags = TaggedItem.objects.filter(object_id=post.id, content_type__pk=content_type.id )
    comments = Comment.objects.filter(content_type=content_type, object_id=post.id)
    cant_delete = False
    for c in comments:
        if c.profile != profile:
            cant_delete = True
            return locals()
    
    user = get_user_object(request)
    profile = get_profile_object(user)

    if post.profile == profile:
        post.delete()
        comments.delete()
    return locals()

@login_required()
@render_to("posts/edit.html")
def edit(request, post_id = None):
    """New posts and edit posts"""
    user = get_user_object(request)
    if user.username=="Anonymous":
        return HttpResponseRedirect("/")

    profile = get_profile_object(user)
    if post_id:

        post = get_object_or_404(Post, pk=post_id)
        post_type = post.post_type.name
        
        if post.profile != profile: # Users can edit only own posts
            return HttpResponseRedirect("/")
        tags = ""
        object_type = ContentType.objects.get_for_model(Post)
        for t in TaggedItem.objects.filter(content_type=object_type, object_id = post.id):
            tags = tags + t.tag.name+","
        print post_type        
        if post_type == "News":
            form = PostForm(instance=post, initial={"tags":tags, "post_type":post_type})
        if post_type == "Question":
            qform = QuestionForm(instance=post, initial={"qtags":tags, "qprofile":post.profile, "qtitle":post.title, "qtext":post.text, "qpost_type":post_type})

    if request.method == "POST": 
        try:
            post_type = request.POST['npost_type']        
        except:
            post_type = request.POST['qpost_type']
        post_type_object = PostType.objects.get(name=post_type)

        if post_id: # edit
            new_post = False
            if post_type == "News":
                form = PostForm(request.POST, instance=post)
            if post_type == "Question":
                form = QuestionForm(request.POST, instance=post)
        else:
            new_post = True
            if post_type == "News":
                form = PostForm(request.POST)
            if post_type == "Question":
                form = QuestionForm(request.POST)
        qform = form
        if form.is_valid():
            if post_type == "News":
                tags = form.cleaned_data['tags'].split(",")
            else:
                tags = form.cleaned_data['qtags'].split(",")

            if post_id: # deleting tags
                new_post = form.save(commit=False)
                object_type = ContentType.objects.get_for_model(Post)
                for t in TaggedItem.objects.filter(content_type=object_type, object_id = post.id):
                    t.delete()
            else:
                new_post = form.save(commit=False)
            new_post.post_type = post_type_object

            if post_type == "News":
                reference_link = form.cleaned_data['reference_link'].strip()
                if len(reference_link)>1:
                    if reference_link.lower()[:4] != 'http':
                        reference_link = "http://" + reference_link
                new_post.reference_link = reference_link
            else:
                new_post.profile = form.cleaned_data['qprofile']
                new_post.text =  form.cleaned_data['qtext']
                new_post.title =  form.cleaned_data['qtitle']
            new_post.save()

            for t in tags:
                if t.strip() != "":
                    tag, c = Tag.objects.get_or_create(name=t.strip().lower())
                    to = TaggedItem(tag=tag, content_object=new_post)
                    to.save()
            if new_post:
                profile.rate = profile.rate + 3
                profile.save()
            return HttpResponseRedirect(new_post.get_absolute_url()) # redirecting to new post
        else:
            print form.errors
            pass # some errors in form
        
    return locals()


@render_to("posts/news_list.html")
def news(request):
    """Display all news for bots   """
    try:
        page_id = int(request.GET.get('p', '1'))
    except ValueError:
        page_id = 1
    post_type = PostType.objects.get(name="News")  # We show only news for bots
    posts = Post.objects.filter(post_type=post_type).select_related().order_by("-publication_date")
    paginator, page, page_range, page_id = prepeare_pagination(posts, request)
    return locals()

@render_to("posts/list.html")
def get_posts(request):
    """Ajah request for new posts. 
         posts_tags = TaggedItem.objects.filter(content_type__pk=object_type.id).distinct().values("object_id", "publication_date").order_by("-publication_date")[:5]
         new_posts = Post.objects.filter(id__in=[p['object_id'] for p in posts_tags]).distinct().order_by('-publication_date')
    """
    if request.is_ajax():
        if request.method == 'POST':
            try:
                page_id = int(request.POST.get('page_id', '1'))
            except ValueError:
                page_id = 1
            post_type = request.POST.get('post_type', 'News')
            post_type = PostType.objects.get(name=post_type)
            
            posts = Post.objects.filter(post_type=post_type).select_related().order_by("-publication_date")
            content_type = ContentType.objects.get_for_model(Post)

           
            p = Paginator(posts, 5)
            try:
                page = p.page(page_id)
            except (EmptyPage, InvalidPage):
                page = [] #p.page(p.num_pages)

            if page:
                comments = Comment.objects.filter(content_type=content_type, object_id__in=[p.id for p in page.object_list]).select_related().order_by("-rate")
            return locals()
    raise Http404

def vote(request, mark): 
    results = {'success':False}
    user = get_user_object(request)

    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        results = {'success':'error', 'id':''}                        
        json = simplejson.dumps(results)
        return HttpResponse(json, mimetype='application/json')

    if request.method == u'GET':
        GET = request.GET
        if GET.has_key(u'pk'):
            post_id = int(GET[u'pk'])
            mark = int(mark)
            if mark !=1 and mark != -1:
                return False
            post = Post.objects.get(pk=post_id)
            vote,c = PostVote.objects.get_or_create(post=post, profile=profile)
            if c:
                vote.mark = str(mark)
                vote.save()
                post.rate = post.rate+mark
                post.save()
                post.profile.rate = post.profile.rate + mark
                post.profile.save()
                results = {'success':post.rate, 'id':post.id}                
            else:
                results = {'success':'already voted', 'id':post.id}                
                
        json = simplejson.dumps(results)
        return HttpResponse(json, mimetype='application/json')

@render_to("view_site.html")
def external(request, link_id):
    """view external url    """
    el = get_object_or_404(ExternalLink, pk=link_id)
    el.views = el.views + 1
    el.save()
    return locals()
