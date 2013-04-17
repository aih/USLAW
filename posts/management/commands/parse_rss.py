import feedparser
try:
    import re2 as re
except:
    import re
from time import time as timer
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils.html import strip_tags
from django.contrib.contenttypes.models import ContentType
from django.db import connection

from users.models import Profile
from posts.models import Post, RssFeed, PostType, ExternalLink
from tags.models import Tag, TaggedItem

class Command(BaseCommand):
    help = """Parse rss feeds"""

    def handle(self, *args, **options):
        post_type = PostType.objects.get(name='News')
        object_type = ContentType.objects.get_for_model(Post)
        #i = 0
        for feed in RssFeed.objects.filter(active=True, last_update__lt=datetime.now()-timedelta(minutes=5)):

            content_updated = False

            if feed.last_update < datetime.now() - timedelta(minutes=feed.frequency):

                #print "Channel: %s " % feed.channel
                t1 = timer()
                try:
                    d = feedparser.parse(feed.channel)
                except UnicodeDecodeError:
                    d = {"entries":[]}
                t2 = timer()
                g = (t2-t1)*1000
                #if g > 10:
                #    print 'Step 2 took %0.3f ms' % g

                #if len(d) == 0:
                #    print "Feed %s is empty" % feed

                for e in d['entries']:
                    t1 = timer()
                    try:
                        content = e.content[0].value
                    except AttributeError:
                        content = e.description

                    ff_re = re.compile(r'(.*?)<div class="feedflare">', re.DOTALL)
                    try:
                        text = ff_re.findall(content)[0]                     
                    except:
                        text = content

                    try:
                        link = e.feedburner_origlink
                    except AttributeError:
                        link = e.link

                    title = strip_tags(e.title)

                    t2 = timer()
                    g = (t2-t1)*1000
                    #if g > 10:
                    #    print 'Step 3 took %0.3f ms' % g
                    p = ExternalLink.objects.filter(url = link)
                    #print link

                    if len(p) == 0:
                        content_updated = True
                        t1 = timer()
                        if feed.channel_label:
                            label = feed.channel_label
                        else:
                            label = " "
                        p = Post(post_type=post_type, title=title, 
                                 reference_link=link, text=text, 
                                 profile=feed.profile, source=label)
                        p.save()

                        #print "New post saved!! %s" %p.title
                        try:
                            for t in e.tags:
                                if len(t.term) < 51:
                                    tag, c = Tag.objects.get_or_create(name=t.term.lower())
                                    to, c = TaggedItem.objects.get_or_create(tag=tag, 
                                                               content_type=object_type, 
                                                               object_id=p.id)
                                    to.save()                        
                        except AttributeError, e:
                            #print e
                            pass

                        tag, c = Tag.objects.get_or_create(name='rss')
                        to, c = TaggedItem.objects.get_or_create(tag=tag, 
                                                  content_type=object_type,
                                                  object_id=p.id)
                        to.save()
                        #for tag in feed[0].tags.all():
                        #    print "Tag:", Tag
                            #to = TaggedItem(tag=tag.name, content_object=p)
                            #to.save()
                        t2 = timer()
                        g = (t2-t1)*1000
                        #if g > 1:
                        #    print 'Step 4 took %0.3f ms' % g

                if content_updated:
                    feed.frequency = feed.frequency - 5
                    if feed.frequency < 5:
                        feed.frequency = 5
                else:
                    feed.frequency = feed.frequency + 5
                feed.last_update = datetime.now()
                feed.save()

        time = 0.0
        for q in connection.queries:
            #print q['sql']
            #print q['time']
            #if len(q['sql'])>200:
            #    print q['sql'][:150]
            time += float(q['time'])
        #print len(connection.queries)
        #print "Total time", time

