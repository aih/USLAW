# -*- coding: utf-8 -*-
"""Tax 26 project. Emailfeed views."""


from django.http import Http404, HttpResponseRedirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import get_object_or_404

from utils.utils import render_to
from emailfeed.models import EmailFeed, FeedPost

@render_to("emailfeed/index.html")
def index(request):
    posts = FeedPost.objects.filter(emailfeed__is_banned=False).order_by("-publication_date")
    try:
        page = Paginator(posts, 50).page(int(request.GET.get('p', 1)))
    except EmptyPage, InvalidPage:
        raise Http404
    return locals()

@render_to("emailfeed/feed.html")
def feed(request, feed_name):
    feed = get_object_or_404(EmailFeed, name=feed_name)
    if feed.is_banned:
        raise Http404
    posts = FeedPost.objects.filter(emailfeed=feed).order_by("-publication_date")
    try:
        page = Paginator(posts, 50).page(int(request.GET.get('p', 1)))
    except EmptyPage, InvalidPage:
        raise Http404

    return locals()

@render_to("emailfeed/feed_post.html")
def feed_post(request, post_id):
    p = get_object_or_404(FeedPost, pk=post_id)
    return locals()


