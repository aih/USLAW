#-*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.core.paginator import Paginator, InvalidPage, EmptyPage 
from django.template import Context, loader
from django.contrib.flatpages.models import FlatPage

from laws.models import *
from posts.models import *

class Command(BaseCommand):
    """
    Create sitemap
    """
    help = """Create sitemap"""
 
    def handle(self, *args, **options):
        #print "Generating sitemap"
        from local_settings import SITE_URL, MEDIA_ROOT

        titles = Title.objects.filter()
        paginator = Paginator(titles, 10000) 
        for p in paginator.page_range:
            try:
                page = paginator.page(p)
            except (EmptyPage, InvalidPage):
                raise
            t = loader.get_template('sitemap.html')
            c = Context(locals())
            f = open(MEDIA_ROOT+"../sitemap/sitemap-%s.xml" % p, "w+")
            f.write(t.render(c))
            f.close()
        all_pages = len(paginator.page_range)
        posts = Post.objects.all()
        paginator = Paginator(posts, 10000) 

        for p in paginator.page_range:
            try:
                page = paginator.page(p)
            except (EmptyPage, InvalidPage):
                raise
            t = loader.get_template('sitemap.html')
            c = Context(locals())
            real_page = p + all_pages
            f = open(MEDIA_ROOT+"../sitemap/sitemap-%s.xml" % real_page, "w+")
            f.write(t.render(c))
            f.close()
        all_pages += len(paginator.page_range)        

        sections = Section.objects.all()
        paginator = Paginator(sections, 10000)

        for p in paginator.page_range:
            try:
                page = paginator.page(p)
            except (EmptyPage, InvalidPage):
                raise
            t = loader.get_template('sitemap.html')
            c = Context(locals())
            real_page = p + all_pages
            f = open(MEDIA_ROOT+"../sitemap/sitemap-%s.xml" % real_page, "w+")
            f.write(t.render(c))
            f.close()
        all_pages += len(paginator.page_range) 


        regulations = Regulation.objects.all()
        paginator = Paginator(regulations, 10000)

        for p in paginator.page_range:
            try:
                page = paginator.page(p)
            except (EmptyPage, InvalidPage):
                raise
            t = loader.get_template('sitemap.html')
            c = Context(locals())
            real_page = p + all_pages
            f = open(MEDIA_ROOT+"../sitemap/sitemap-%s.xml" % real_page, "w+")
            f.write(t.render(c))
            f.close()
        all_pages += len(paginator.page_range) 

        rulings = IRSRevenueRulings.objects.all()
        paginator = Paginator(rulings, 10000)

        for p in paginator.page_range:
            try:
                page = paginator.page(p)
            except (EmptyPage, InvalidPage):
                raise
            t = loader.get_template('sitemap.html')
            c = Context(locals())
            real_page = p + all_pages
            f = open(MEDIA_ROOT+"../sitemap/sitemap-%s.xml" % real_page, "w+")
            f.write(t.render(c))
            f.close()
        all_pages += len(paginator.page_range) 


        leters = IRSPrivateLetter.objects.all()
        paginator = Paginator(leters, 10000)
        for p in paginator.page_range:
            try:
                page = paginator.page(p)
            except (EmptyPage, InvalidPage):
                raise
            t = loader.get_template('sitemap.html')
            c = Context(locals())
            real_page = p + all_pages
            f = open(MEDIA_ROOT+"../sitemap/sitemap-%s.xml" % real_page, "w+")
            f.write(t.render(c))
            f.close()
        all_pages += len(paginator.page_range) 



        pls = PubLaw.objects.all()
        paginator = Paginator(pls, 10000)
        for p in paginator.page_range:
            try:
                page = paginator.page(p)
            except (EmptyPage, InvalidPage):
                raise
            t = loader.get_template('sitemap.html')
            c = Context(locals())
            real_page = p + all_pages
            f = open(MEDIA_ROOT+"../sitemap/sitemap-%s.xml" % real_page, "w+")
            f.write(t.render(c))
            f.close()
        all_pages += len(paginator.page_range) 



        all_pages += 1
        all_pages = [p for p in range(1, all_pages)]
        t = loader.get_template('sitemap_index.html')
        c = Context(locals())
        f = open(MEDIA_ROOT+"../sitemap/sitemap-index.xml", "w+")
        f.write(t.render(c))
        f.close()

        
