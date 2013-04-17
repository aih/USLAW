# Create your views here.

from django.shortcuts import get_object_or_404
from django.utils import simplejson
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required

from utils.utils import render_to
from users.models import Profile, get_user_object, get_profile_object
from comment.models import *

@login_required
def del_comment(request, comment_id):
    user = get_user_object(request)
    c = get_object_or_404(Comment, pk=comment_id)
    if c.profile.user == user:
        url = c.get_absolute_url()
        c.delete()
    else:
        url = "/users/error/"
    return HttpResponseRedirect(url)

@login_required
@render_to("comment/edit.html")
def edit_comment(request, comment_id):
    user = get_user_object(request)
    c = get_object_or_404(Comment, pk=comment_id)
    if c.profile.user == user:
        form = CommentForm(instance=c)
        if request.method=='POST':
            form = CommentForm(request.POST, instance=c)
            if form.is_valid():
                form.save()
                url = c.get_absolute_url()
                return HttpResponseRedirect(url)
        else:
            return locals()
    else:
        url = "/users/error/"
        return HttpResponseRedirect(url)


def add_comment(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            if request.POST["email"] != "":
                #print "SPAM"
                return HttpResponseRedirect("/")
            user = get_user_object(request)

            c_text=form.cleaned_data["text"]
            if form.cleaned_data["parent"]!="" and form.cleaned_data["parent"]:
                parent = Comment.objects.get(pk__exact=int(form.cleaned_data["parent"]))
            else:
                parent = None
            p = get_profile_object(user)
            if p == False: # Profile does not exists
                return HttpResponseRedirect("/")
            object_id = form.cleaned_data['object_id']
            content_type = form.cleaned_data['content_type']
            c = Comment(text = c_text, profile=p, content_type=content_type, object_id=object_id, parent=parent)
            c.save()
            next = form.cleaned_data["next"]
            p.rate = p.rate + 1
            p.save()
            return HttpResponseRedirect(next+"#"+str(c.id))
        else:
            print form.errors
            pass


    return HttpResponseRedirect("/")

def vote(request, mark): #, wallpapper_id, mark):
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
            comment_id = int(GET[u'pk'])
            mark = int(mark)
            if mark !=1 and mark != -1:
                return False
            comment = Comment.objects.get(pk=comment_id)
            vote,c = Vote.objects.get_or_create(comment=comment, profile=profile)
            if c:
                vote.mark = str(mark)
                vote.save()
                comment.rate = comment.rate+mark
                comment.save()
                comment.profile.rate = comment.profile.rate + mark
                comment.profile.save()
                results = {'success':comment.rate, 'id':comment.id}                
            else:
                results = {'success':'already voted', 'id':comment.id}                
                
        json = simplejson.dumps(results)
        return HttpResponse(json, mimetype='application/json')

def follow(request): #, wallpapper_id, mark):
    results = {'success':False}
    user = get_user_object(request)
    profile = get_profile_object(user)
    if profile == False or user.username == 'Anonymous':
        results = {'success': 'You must be signed in'}                        
        json = simplejson.dumps(results)
        return HttpResponse(json, mimetype='application/json')

    if request.method == u'GET':
        GET = request.GET
        if GET.has_key(u'pk'):
            try:
                object_id = int(GET[u'pk'])
                content_type_id = int(GET[u'ct'])
                action = GET[u'follow']
            except ValueError, IndexError:
                results = {'success':'Internal Error'}                
            else:
                ct = ContentType.objects.get(pk = content_type_id)
                co = FollowObject.objects.filter(profile = profile, object_id=object_id, content_type = ct).count()
                
                if co == 0:
                    if action == 'follow':
                        f = FollowObject(profile = profile, object_id=object_id, content_type = ct)
                        f.save()
                        results = {'success':'You are now following updates'}
                else:
                    if action == 'unfollow':
                        FollowObject.objects.filter(profile = profile, object_id=object_id, content_type = ct).delete()
                        results = {'success':'You are now not following updates'}
                    else:
                        results = {'success':'You are already following updates'}
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')



# TODO:
#@login_required()
#def del_comment(request, comment_id):
#    if request.user.is_staff:
#        c = Comment.objects.get(id__exact=comment_id)
#        c.delete()
#    return HttpResponseRedirect('/')



