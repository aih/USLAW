# -*- coding: utf-8 -*-
# Tax26.com Project.
# Users views
#

import urllib
import urlparse 
import hashlib
from random import randint
import oauth2 as oauth
from linkedin import linkedin

from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils import simplejson
from django.conf import settings as django_settings

from utils.utils import render_to
from posts.models import PostForm, Post, PostType, QuestionForm
from tags.models import TaggedItem, Tag
from users.models import *
from laws.models import *
from laws.forms import SearchForm
from comment.models import Comment
from emailfeed.models import FeedPost


@render_to("users/home.html")
def home(request):
    """Home page for users. With news and Q/A section"""
    active_section = "home"
    user = get_user_object(request)
    object_type = ContentType.objects.get_for_model(Post)

    searchform = SearchForm()
    best_questions = Post.objects.filter(post_type__name='Question').order_by('-rate')[:5]
    best_news = Post.objects.filter(post_type__name='News').order_by('-rate')[:5]

    profile = get_profile_object(user)
    if profile==False:
        return HttpResponseRedirect("/")
    display_linkedin_connect, c = Option.objects.get_or_create(user=user, name='linkedin_connect')
    if c:
        init_options(user)
        display_linkedin_connect.bvalue = True
        display_linkedin_connect.save()
    if display_linkedin_connect.bvalue and profile.public_profile=="":
        notice = "Connect with your LinkedIn account to add your profile (We don't need access to your LinkedIN password.). To start, click <a class='under' href='/users/linkedin-connect/'>here</a>. To change notice settings click <a class='under' href='/users/settings'>here</a>."
    if profile:
        object_type = ContentType.objects.get_for_model(Profile)
        tags = TaggedItem.objects.filter(object_id=profile.id, content_type__pk=object_type.id )
        tags_list = ""
        #for t in tags:
        #    tags_list = tags_list+t.tag.name+","
        qpost_type = PostType.objects.get(name="Question")
        post_type = PostType.objects.get(name="News")
        form = PostForm(initial={"profile":profile, "npost_type": post_type})
        qform = QuestionForm(initial={"qprofile":profile, "qpost_type":qpost_type})
    return locals()

def login_user(request, **kwargs):
    """
    Login user and return User or False.
    """
    user = authenticate(**kwargs)
    if user is not None:
        if user.is_active:
            login(request, user)
    else:
        user = False
    return user

@render_to("registration/login.html")
def do_login(request):
    form = LoginForm()
    if request.method=='POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            password = form.cleaned_data['password']
            user = authenticate(username=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                else:
                    p = get_profile_object(user)
                    user = False
                    user_inactive = True
            else:
                login_error = True
        else:
            login_error = True

    return locals()


@render_to('registration/reg.html')
def reg(request):
    """Registration procedure."""
    #public_profile = request.session.get('public_profile', False)
    #profile = request.session.get('profile', False)
    #if profile == False or public_profile == False:
    #    return HttpResponseRedirect("/users/error/?invalid_profile")
    errors = []
    if request.method == "POST":
        form = RegForm(request.POST) # A form bound to the POST data
        if form.is_valid():
            password = form.cleaned_data['password']
            rpassword = form.cleaned_data['rpassword']
            email = form.cleaned_data['email'].lower()
            tags = form.cleaned_data['areaofinterest']
            c_user = User.objects.filter(email=email)
            if len(c_user)>0:
                errors.append('This email already used.')

            if len(errors) == 0:
                user = User.objects.create_user(username=email, email=email, password=password)
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.is_active = False
                user.save() 
                
                p = Profile(user=user, rate=0, picter="", public_profile = "",
                            headline = "", location = "", industry = "", summary = "",
                            specialties = "", interests = "",
                            honors = "", linkedin_id = "")
                p.save()

                for t in tags:  # Adding tags to users profile
                    tag, c = Tag.objects.get_or_create(name=t)
                    to = TaggedItem(tag=tag, content_object=p)
                    to.save()
                
                user = False
                registered = True
                return locals()#  HttpResponseRedirect('/users/login/')
            else:
                #form = RegForm()
                return locals()
        return locals()
    else:
        form = RegForm()
    return locals()

@render_to('search/last_search.html')
@login_required()
def last_search(request): 
    user = get_user_object(request)
    search = Search.objects.filter(user=user).order_by("-publication_date")[:10]
    return locals()

@render_to('registration/start_reg.html')
def start_reg(request): 
    return locals()

@render_to('registration/start_reg.html')
def linkedinlogin(request, request_type = 0):
    consumer_key = settings.LinkedInAPIKey
    consumer_secret = settings.LinkedInSecretKey
    callback_url = settings.callbackurl 

    request_token_url =	'https://api.linkedin.com/uas/oauth/requestToken'
    authorize_url = 	'https://www.linkedin.com/uas/oauth/authenticate'
    api = linkedin.LinkedIn(consumer_key, consumer_secret, callback_url)
    try:
        result = api.requestToken()
    except:
        result = False

    if result!=True:
        error = api.getRequestTokenError()
        return HttpResponseRedirect("/users/error/?error=linkedin_api_error") 
    t = TmpToken(token =  api.request_token, token_secret = api.request_token_secret, request_type=request_type)
    t.save()
    return HttpResponseRedirect(api.getAuthorizeURL())
    
@render_to("registration/reg.html")
def linkedin_callback(request):
    """Linkedin CallBack """
    if request.GET.has_key('oauth_problem'):
        return HttpResponseRedirect("/users/error/?error=%s" % request.GET['oauth_problem'])
    oauth_verifier = request.GET['oauth_verifier']
    oauth_token = request.GET['oauth_token']
    t = TmpToken.objects.get(token=oauth_token)
    consumer_key = settings.LinkedInAPIKey
    consumer_secret = settings.LinkedInSecretKey
    callback_url = settings.callbackurl 

    api = linkedin.LinkedIn(consumer_key, consumer_secret, callback_url)
    result = api.accessToken(t.token, t.token_secret, oauth_verifier)
    if result==False or result==None:
        return HttpResponseRedirect("/users/error/?error=linkdenin_error")#
    else:
        
        profile = api.GetProfile(member_id=None, url=None, fields=["public-profile-url", "first-name", "last-name",])
        if t.request_type > 0: # Connect or update
            public_profile = api.GetProfile(url = profile.public_url, 
                                        fields=[ "publications", "languages", "first-name", "last-name", "id", "picture-url", "headline", "location", 
                                                "industry", "summary", "specialties", "interests", "honors" , "positions", 
                                                "educations", "current_status", "skills", "certifications", ])
            if public_profile==False:
                return HttpResponseRedirect("/users/error/?error=linkedin_public_profile")#  TODO: add error handling
        else: # Login
            try:
                p = Profile.objects.get(public_profile = profile.public_url)             #
            except Profile.DoesNotExist:
                return HttpResponseRedirect("/users/error/?error=linkedin_public_profile")#  TODO: add error handling
            user = login_user(request, linkedin_profile=profile.public_url)
            if user:
                if user.is_active == False:
                    user = False
                    not_active = True # New user, email not confirmed                
                    return locals()
                return locals()
        user = get_user_object(request)
        try:
            p = Profile.objects.get(user = user)             #public_profile=profile.public_url
        except Profile.DoesNotExist:
            p = Profile(user=user, rate=0, picter="", public_profile = "",
                        headline = "", location = "", industry = "", summary = "",
                        specialties = "", interests = "",
                        honors = "", linkedin_id = "")
            p.save()

        p.picter=public_profile.picture_url
        p.public_profile = profile.public_url
        p.headline = public_profile.headline
        p.location = public_profile.location
        p.industry = public_profile.industry
        p.summary = public_profile.summary
        p.specialties = public_profile.specialties
        p.interests = public_profile.interests
        p.honors = public_profile.honors
        p.linkedin_id = public_profile.id
        p.save()

        p.position.all().delete()
        p.education.all().delete()

        for pos in public_profile.positions:
            position = Position(title=pos.title, summary=pos.summary, start_date=pos.start_date, 
                                end_date=pos.end_date, company=pos.company.name, company_type=pos.company.type, 
                                company_size = pos.company.size, company_industry=pos.company.industry, company_ticker=pos.company.ticker)
            position.save()
            p.position.add(position)
            position.id=None

        for e in public_profile.educations:
            e = Education(school_name=e.school_name, degree=e.degree, activities=e.activities, notes=e.notes, 
                          start_date=e.start_date, end_date=e.end_date)
            e.save()
            p.education.add(e)
            e.id = None
        return HttpResponseRedirect(p.get_absolute_url())

    return locals()

@login_required()
def linkedin_connect(request):
    """Connect profile with linkedIn profile """
    return linkedinlogin(request,1 )

@login_required()
def linkedin_update(request):
    """Update profile information from linkedIn profile """
    return linkedinlogin(request, 2)


@render_to("registration/error.html")
def error(request):
    error = request.GET.get('error', 'none')
    return locals()

@render_to("index.html")
def main_index(request):
    active_section = "home"
    user= get_user_object(request)
    post_type = PostType.objects.get(name="News")  # We show only news for bots
    news = Post.objects.filter(post_type=post_type).select_related().order_by("-publication_date")[:5]

    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        pass
    else:
        if user.username !="Anonymous":
            return HttpResponseRedirect("/users/home/")

    posts = FeedPost.objects.filter(emailfeed__is_banned=False).order_by("-publication_date")
    page = Paginator(posts, 50).page(1)

    return locals()


@render_to("users/password_reset.html")
def password_reset(request):
    form = PasswordRestoreForm()
    link_hash = request.GET.get('link_hash', '')
    if link_hash and len(link_hash)>0:
        try:
            rp = RestorePasswordLink.objects.get(link_hash=link_hash)
        except RestorePasswordLink.DoesNotExist:
            error = "This password restore link not exist"
        else:
            password_restore = True
            form = NewPasswordForm(initial={"link_hash":link_hash})

    if request.method == 'POST':
        form = PasswordRestoreForm(request.POST)
        if "email" in request.POST:
            if form.is_valid():
                try:
                    user = User.objects.get(email = form.cleaned_data['email'].lower())
                except User.DoesNotExist:
                    error = "User with this email does not exist in our database"
                else:
                    h = hashlib.new('sha256')
                    h.update(user.email)
                    h.update(str(randint(999, 999999999999)))
                    link_hash = h.hexdigest()
                    r = RestorePasswordLink(user = user, link_hash=link_hash)
                    r.save()
                    link_sended = True
                    user = False
        elif "link_hash" in request.POST:
            
            form = NewPasswordForm(request.POST)
            password_restore = True
            if form.is_valid():
                try:
                    rp = RestorePasswordLink.objects.get(link_hash=form.cleaned_data['link_hash'])
                except RestorePasswordLink.DoesNotExist:
                    error = "This password restore link not exist"
                else:
                    rp.user.set_password(form.cleaned_data['password'])
                    rp.user.save()
                    try:
                        p = Profile.objects.get(user=rp.user)
                    except Profile.DoesNotExist:
                        pass
                    else:
                        p.save()
                    rp.delete()
                    password_changed = True
                    password_restore = False
    return locals()

@render_to("registration/confirm.html")
def confirm(request, ec_token):
    ec = get_object_or_404(EmailConfirm, token=ec_token)
    profile = get_object_or_404(Profile, user=ec.user)
    profile.email_active = True
    profile.save()
    profile.user.is_active=True
    profile.user.save()
    ec.delete()
    return locals()

@render_to("users/user_posts.html") #TODO: move this view post module!
def user_posts(request, profile_id):
    user_profile = get_object_or_404(Profile, pk=profile_id)
    searchform = SearchForm()
    user= get_user_object(request)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        pass
    try:
        p_type = request.GET.get('type', False)
    except:
        p_type = False
    if p_type:
        posts = Post.objects.filter(profile=user_profile, post_type__name=p_type)
    else:
        posts = Post.objects.filter(profile=user_profile)
    try:
        page_id = int(request.GET.get('p', 1))        
    except ValueError:
        page_id = 1

    paginator = Paginator(posts, 20)
    try:
        page = paginator.page(page_id)
    except EmptyPage:
        paginator = None

    return locals()

@render_to("users/profile.html")
def profile(request, profile_id):
    active_section = "profile"
    p = get_object_or_404(Profile, pk=profile_id)
    user = get_user_object(request)
    profile = get_profile_object(user)
    searchform = SearchForm()
    news = Post.objects.filter(profile=p, post_type__name='News').count()
    questions = Post.objects.filter(profile=p, post_type__name='Questions').count()
    comments = Comment.objects.filter(profile=p).count()
    return locals()

@render_to("users/options.html")
def profile_settings(request):
    active_section = "profile"
    user = get_user_object(request)
    profile = get_profile_object(user)
    # get options:
    init_options(user)
    display_linkedin_connect = Option.objects.get(user=user, name='linkedin_connect')
    display_help_bubbles = Option.objects.get(user=user, name='display_help_bubbles')

    searchform = SearchForm()
    object_type = ContentType.objects.get_for_model(Profile)
    tags_ = TaggedItem.objects.filter(object_id=profile.id, content_type__pk=object_type.id)
    if request.method=="POST":
        form_type = request.POST.get('form_type', '')
        if form_type == 'options':
            display_linkedin_connect = Option.objects.get(user=user, name='linkedin_connect')
            display_help_bubbles = Option.objects.get(user=user, name='display_help_bubbles')
            display_linkedin_connect.bvalue = request.POST.get('display_linkedin_connect', False)
            display_linkedin_connect.save()

            display_help_bubbles = Option.objects.get(user=user, name='display_help_bubbles')
            display_help_bubbles.bvalue = request.POST.get('display_help_bubbles', False)
            display_help_bubbles.save()

        else:
            form = AreaOfInterestForm(request.POST)
            if form.is_valid():
                tags = form.cleaned_data['areaofinterest']
                tagged_items = TaggedItem.objects.filter(object_id=profile.id, content_type__pk=object_type.id)
                tagged_items.delete()
                for t in tags:
                    to = TaggedItem(tag=t, content_object=profile)
                    to.save()

    tags_ = TaggedItem.objects.filter(object_id=profile.id, content_type__pk=object_type.id)
    tags = []
    for t in tags_:
        tags.append(t.tag)
    form = AreaOfInterestForm(initial={"areaofinterest": tags,})
    return locals()


@login_required
@render_to("users/password_change.html")
def password_change(request):
    form = ChangePasswordForm()
    user = get_user_object(request)
    profile = get_profile_object(user)
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            try:
                p = Profile.objects.get(user=user)
            except Profile.DoesNotExist:
                return HttpResponseRedirect("/users/error/?invalid_profile")
            else:
                check_user = login_user(request, user.email, form.cleaned_data['password'])
                if not check_user:
                    error = "Old password is incorrect"
                else:
                    user.set_password(form.cleaned_data['password'])
                    user.save()
                    password_changed = True
    return locals()

@render_to("registration/resend_confirmation.html")
def resend_email(request):
    if request.method == "POST":
        try:
            p_id = request.POST.get('profile_id', False)
        except:
            pass
        else:
            try:
                p = Profile.objects.get(pk=p_id)                
            except Profile.DoesNotExist:
                error = "Profile does not exists"
            else:
                p.resend_confirmation()
    user = False
    return locals()

@render_to("users/profiles-list.html")
def redirect_profile(request):
    """Find user profile and redirect to  """
    user = get_user_object(request)
    if user:
        profile = get_profile_object(user)
        if profile:
            return HttpResponseRedirect(profile.get_absolute_url())
    profiles = Profile.objects.filter(user__is_active = True)
    return locals()


def get_avatar_info(request):
    """Ajax request for avatar info
    Return json posts.
    """
    if request.is_ajax():
        if request.method == 'GET':
            p_id = request.GET['id']
            p = Profile.objects.get(pk=p_id)
            #json = simplejson({'user':p.user.first_name+p.user.last_name,})
            return HttpResponse("123123")#json, mimetype='application/json')
