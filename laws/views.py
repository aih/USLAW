# -*- coding: utf-8 -*-
"""Tax 26 project. US Law views."""

try:
    import re2 as re
except:
    import re
import random  
import hashlib
import lxml.html
import lxml.etree
from datetime import datetime

from django.http import Http404, HttpResponseRedirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
#from django.utils import simplejson
from django.db import connection
from django.core import serializers
from django.db.models import Q
from django.core.urlresolvers import NoReverseMatch
from djangosphinx.models import SphinxQuerySet
from django.shortcuts import render

from laws.models import *
from laws.forms import *
from users.models import Search, Profile, get_user_object, get_profile_object
from comment.models import Comment, CommentForm
from utils.utils import render_to, get_page_range, prepeare_pagination
from tags.models import TaggedItem, TaggedItemForm, OutdatedResource
from posts.models import Post

#@login_required

def title_text_ajax(request, title_id):
    """Load Title object trough  ajah"""
    title = get_object_or_404(Title, pk=title_id)
    return render(request, "laws/title_text_ajax.html", {"title":title})

def topics(request):
    """UCS Topics view"""
    topics = USCTopic.objects.all().order_by("order")
    return render(request, "laws/title_text_ajax.html", {"topics":topics})

def load_topic(request):
    """Load topic object"""
    pk = int(request.GET.get("pk", False))
    topic = get_object_or_404(USCTopic, pk=pk)
    title = Title.objects.get(title='26') #FIXME: Only Title 26 for now. 
    sections = Section.objects.filter( \
        int_section__gte=topic.first_section.int_section, 
        int_section__lte=topic.last_section.int_section, 
        top_title=title)
    return render(request, "laws/section-list.html", {"pk":pk, "topic":topic,
                                                      "title":title,
                                                      "sections":sections})

def section_redirect_map (request, title, pk):
    """Redirect for links from Tax-Map to sections"""
    s = get_object_or_404(Section, pk=pk)
    try:
        url = s.get_absolute_url() # FIXME
    except:
        raise Http404
    return HttpResponseRedirect(url)

def section_redirect(request, title, section):
    """Redirect to section using title and section names
    For example: title='26', section='1' """
    try:
        title = Title.objects.get(title=title, parent=None)
    except Title.DoesNotExist:
        pass
    else:
        try:
            section = section.encode("utf-8").replace("–", "-")
            s = Section.objects.get(section = section, top_title=title)
        except Section.DoesNotExist:
            pass
        except Section.MultipleObjectsReturned:
            url = reverse("multiple_sections_page", 
                          kwargs={'title':str(title.title), 
                                  'section':section})
            return HttpResponseRedirect(url)
        else:
            return HttpResponseRedirect(s.get_absolute_url()) # FIXME: use reverse
    raise Http404

def title_redirect(request, title):
    """Redirect to Title object using title name (like Title='26')"""
    title = get_object_or_404(Title, title=title, parent=None)
    return HttpResponseRedirect(title.get_absolute_url()) # FIXME use reverse


def target_to_section(target):
    """Return - object (title or section), 
    type (title or section), psection or none"""

    redirect = False
    if "ref-unnamedact-" in target:
        target = target.replace("ref-unnamedact-", "").split("/")
        #target = target.replace("ref-namedact-", "")
        if len(target) > 1:
            sub_target = target[1]
            if "(" in sub_target:
                psection = sub_target[sub_target.find("("):]
                sub_target = sub_target[:sub_target.find("(")]
            else:
                psection = ""
        else:
            sub_target = False
        target = target[0]
        
        nas = NamedStatute.objects.filter(title__iexact=target)
        if len(nas) > 0:
            for n in nas:
                if sub_target and n.top_title: #  There are link to section of the act
                    try:
                        section = Section.objects.get(top_title=n.top_title, 
                                                      section=sub_target)
                    except (Section.DoesNotExist, Section.MultipleObjectsReturned):
                        pass
                    else:
                        return section, "Section", psection
                if n.section is not None:
                    return n.section, "Section", ""
                if n.top_title is not None:
                    return n.top_title, "Title", ""
            return nas[0], "NamedAct", ""
        redirect = True

    if "ref-namedact-" in target:
        target = target.replace("ref-namedact-", "").split("/")
        if len(target) > 1:
            sub_target = target[1]
            if "(" in sub_target:
                psection = sub_target[sub_target.find("("):]
                sub_target = sub_target[:sub_target.find("(")]
            else:
                psection = ""
        else:
            sub_target = False
        target = target[0]
        
        nas = NamedStatute.objects.filter(title__iexact = target)
        if len(nas) > 0:
            for n in nas:
                if sub_target and n.top_title: #  There are link to section of the act
                    try:
                        section = Section.objects.get(top_title=n.top_title, 
                                                      section=sub_target)
                    except (Section.DoesNotExist, Section.MultipleObjectsReturned):
                        pass
                    else:
                        return section, "Section", psection
                if n.section is not None:
                    return n.section, "Section", ""
                if n.top_title is not None:
                    return n.top_title, "Title", ""
            return nas[0], "NamedAct", ""
        redirect = True
    if "ref-PL-" in target:
        target = target.replace("ref-PL-", "")
        redirect = True
    if "ref-title-" in target:
        target = target.replace("ref-title-", "")

    if redirect:
        return target, 'NOTIMPLEMENTED', False

    match = re.match(r'^(?P<title>[\w\-]+?)/(?P<section>.*?)$', target)
    match_title = re.match(r'^(?P<title>[\w\-]*?)$', target)
    section_found = False
    psection = False

    if match:
        title = match.group('title')
        top_title = True
        try:
            title = Title.objects.get(title=title, parent=None)
        except Title.DoesNotExist:
            return False, False, False

        if match.group('section'):
            section = match.group('section')
            section = section.encode("utf-8").replace("–", "-")
            if "id-" in section: # Sub Title
                try:
                    title = Title.objects.get( \
                        pk=section.replace("id-","").replace("/", ""))
                except Title.DoesNotExist:
                    return False, False, False
                else:
                    return title, 'Title', False

            if "(" in section:
                psection = section[section.find("("):]
                section = section[:section.find("(")]
            try:
                if top_title:
                    try:
                        section = Section.objects.get(section=section,
                                                  top_title=title)
                    except Section.MultipleObjectsReturned:
                        return False, False, False
                else:
                    section = Section.objects.get(section=section, 
                                                  title=title)
            except Section.DoesNotExist:
                return False, False, False
            else:
                section_object = section
                section_found = True
        else:
            return title, 'Title', False

    elif match_title:
        title = match_title.group('title')
        try:
            title = Title.objects.get(title=title, parent=None)
        except Title.DoesNotExist:
            return False, False, False
        return title, 'Title', False

    if section_found:
        return section_object, 'Section', psection
    else:
        return False, False, False

def target(request, target):
    """This view used for statutes extracted links """

    object_, type_, psection = target_to_section(target)
    if not object_:
        raise Http404

    if type_ == 'Title':
        return HttpResponseRedirect(object_.get_absolute_url())

    if type_ == "NOTIMPLEMENTED": # redirect such links to search
        return HttpResponseRedirect( \
            "/laws/search/?query=%s&where=everywhere&page=1" % object_) # FIXME

    if psection:
        #print "[%s], [%s], [%s]" % (psection, type_, object_)
        subsections = Subsection.objects.filter(section=object_, 
                           subsection__startswith=psection).order_by('part_id')
        if len(subsections) < 2: #
            try:
                first = Subsection.objects.filter(section=object_,
                                                   subsection=psection).order_by("part_id")[0]
                last = Subsection.objects.filter(section=object_,
                                               level=first.level,
                                              part_id__gt=first.part_id\
                                              ).exclude(subsection='').order_by("part_id")[0]
            except IndexError:
                pass
            else:
                subsections = Subsection.objects.filter(section=object_,
                                          part_id__gte=first.part_id,
                                          part_id__lt=last.part_id).order_by("part_id")
        if len(subsections) == 0:
            subsections = Subsection.objects.filter(section=object_) 
    else:
        subsections = Subsection.objects.filter(section=object_) 
    if request.GET.get('context', None) == "hoverbubble":
        if type_ == 'NamedAct':
            return render_to_response("laws/named_act_hoverbubble.html", 
                                      {"namedact":object_, },  
                                      context_instance=RequestContext(request))
        elif type_ == "Section":
            if psection:
                return render_to_response("laws/sub_section.html", 
                                          {"subsections":subsections, },  
                                          context_instance=RequestContext(request))
            else:
                return render_to_response("laws/section_hoverbubble.html", 
                                          {"subsections":subsections, },  
                                          context_instance=RequestContext(request))
    else:
        if len(subsections) > 0:
            return HttpResponseRedirect("%s#%s" % (object_.get_absolute_url(), psection))
        else:
            return HttpResponseRedirect(object_.get_absolute_url())


def hoverbubble(request):
    """This view used for NEW statutes extracted links"""
    section = request.GET.get('section', False)
    title = request.GET.get('title', False)
    psection = request.GET.get('psection', False)
    if title: # If title provided - redirect user to this title
        title = get_object_or_404(Title, title=title)
        return HttpResponseRedirect(title.get_absolute_url())

    section = get_object_or_404(Section, pk=section) 
    if request.GET.get('context', None) != "hoverbubble":
        return HttpResponseRedirect(section.get_absolute_url())

    if psection:
        subsection = Subsection.objects.filter(section=section, 
                                               subsection__iexact=psection)[0]
    else:
        subsection = Subsection.objects.filter(section=section, 
                                               subsection='')[0]
    if psection != False:
        return render_to_response("laws/sub_section.html", 
                                  {"subsection":subsection,'section':section},  
                                  context_instance=RequestContext(request))
    else:
        return render_to_response("laws/section_hover.html", 
                                  {"subsection":subsection,'section':section},  
                                  context_instance=RequestContext(request))

def print_it(request, section_url, section_id, psection=None):
    """View for printing sections"""
    section = get_object_or_404(Section, url=section_url, pk=section_id)
    #if psection:
    #    subsections = Subsection.objects.filter(section=section, 
    #                                            subsection__startswith=psection)
    #else:
    subsections = Subsection.objects.filter(section=section).order_by("part_id")
    additional_sections = SectionAdditional.objects.filter( \
                             section=section).order_by('order')
    return render(request, "laws/print.html",
                  {"section":section,
                   "subsections":subsections,
                   "additional_sections":additional_sections})

def preview_section(request, section_id):
    """Preview section"""
    try:
        section = Section.objects.get(pk=section_id)
        subsection = Subsection.objects.filter(section=section, 
                                               ).order_by("part_id")[0]
    except Section.DoesNotExist, Subsection.DoesNotExist:
        section = False
        
    return render(request, "laws/preview_section.html",
                  {"section": section,
                   "subsection":subsection})
                                                         

def section(request, title, section, section_id, psection=None):
    """Section View"""
    active_section = 'browse'
    form = CommentForm()
    searchform = SearchForm()
    user = get_user_object(request)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        pass
    
    section = get_object_or_404(Section, pk=section_id)
    try:
        section_url = section.get_absolute_url()
    except NoReverseMatch:
        raise Http404

    namedacts = NamedStatute.objects.filter(section=section)
    title = section.title
    subsections = Subsection.objects.filter(section=section).order_by("part_id")
    additional_sections = SectionAdditional.objects.filter( \
                             section=section).order_by('order')
    regulations = Regulation.objects.filter(sections=section).order_by("order_1", "order_2", "order_3")
    publaws = Classification.objects.filter(section=section)
    object_ = section
    content_type = ContentType.objects.get_for_model(Section)
    comment_form = CommentForm(initial={'content_type':content_type})
    comments = Comment.objects.filter(content_type=content_type, 
                              object_id=object_.id).order_by("publication_date")
    tags = TaggedItem.objects.filter(object_id=object_.id, 
                                     content_type__pk=content_type.id )
    outdated = OutdatedResource.objects.filter(object_id=object_.id, 
                                      content_type__pk=content_type.id ).count()
    outdated_by_user = OutdatedResource.objects.filter(object_id=object_.id, 
                                    content_type__pk=content_type.id, user=user)
    if outdated == 0:
        outdated = False
    tagsform = TaggedItemForm(initial={"next":section_url, 
                                       "content_type":content_type.id, 
                                       "object_id":object_.id})
    return render(request, "laws/section.html", locals())


def title_index(request, title_url, title_id):
    """Title Index - list of Titles"""
    active_section = 'browse'
    searchform = SearchForm()
    user = get_user_object(request)
    profile = get_profile_object(user)
    title = get_object_or_404(Title, pk=title_id)
    titles = Title.objects.filter(parent=title).order_by("int_title")
    parts = Section.objects.filter(title=title).order_by('int_section')
    nexttitles = Title.objects.filter(parent=title)
    paginator, page, page_range, page_id = prepeare_pagination(parts, request)
    return render(request, "laws/index.html", locals())

def index(request):
    """Laws Index page"""
    active_section = 'browse'
    searchform = SearchForm()
    titles = Title.objects.filter(parent=None).order_by("int_title")
    user = get_user_object(request)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        pass
    return render(request, "laws/index.html", locals())

def ajah_search(request):  # TODO: Not used view. Maybe remove it?
    """Ajax search"""
    if request.method == u'GET':
        GET = request.GET
        if GET.has_key(u'query'):
            if GET['query'].strip()=="":
                results = None
            else:
                dnow = datetime.now()
                main_query = Subsection.search.query(GET['query'])
                #for r in main_query:
                    #print r.section, "=>", r.subsection

                s = Search.objects.filter(user=get_user_object(request), 
                                          text=GET['query']).delete()
                s = Search(user=get_user_object(request), text=GET['query'], 
                           publication_date=dnow)
                s.save()
                if GET.has_key(u'page'):
                    page_id = GET['page']
                else:
                    page_id = 1
                #main_query = SearchQuerySet().filter(content=GET['query'])
                p_main = Paginator(main_query, 5)
                main_result = p_main.page(page_id)

                next_page = main_result.has_next()
                previous_page = main_result.has_previous()

    return render_to_response("search/search_ajah.html", locals(),
                              context_instance=RequestContext(request))


def search(request):
    """Search Page"""
    active_section = 'search'
    user = get_user_object(request)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = None
    paginator = None
    if request.method == u'GET' and "where" in request.GET:
        searchform = SearchForm(request.GET)
        searchform.fields['where'].widget = forms.Select( \
            choices=SearchForm.SEARCH_CHOICES, 
            attrs={"class":"right_btn", "style":""})
        if searchform.is_valid():
            query = searchform.cleaned_data['query']
            where = searchform.cleaned_data['where']
            date_sort = searchform.cleaned_data['date_sort']
            if not where:
                where = "everywhere"
            dnow = datetime.now()
            usc_re = re.compile(r'(.*?)\s?u\.?s\.?c\.?\s?(.*?)$', re.IGNORECASE)
            usc_result = usc_re.findall(query)
            if len(usc_result) > 0:
                try:
                    section = Section.objects.get( \
                        section=usc_result[0][1].strip(), 
                        top_title__title=usc_result[0][0].strip())
                except Section.DoesNotExist, Section.MultipleObjectsReturned:
                    pass
                else:
                    return HttpResponseRedirect(section.get_absolute_url())
                
            cfr_re = re.compile(r'(.*?)cfr(.*?)$', re.IGNORECASE)
            cfr_result = cfr_re.findall(query)

            if len(cfr_result) > 0:
                try:
                    regulation = Regulation.objects.get( \
                        section=cfr_result[0][1].strip())
                except Regulation.DoesNotExist:
                    try:
                        regulation = Regulation.objects.get( \
                            section="1."+cfr_result[0][1].strip())
                    except Regulation.DoesNotExist:
                        pass
                    else:
                        return HttpResponseRedirect(regulation.get_absolute_url())
                else:
                    return HttpResponseRedirect(regulation.get_absolute_url())
            
            if user:
                s = Search.objects.filter(user=get_user_object(request), 
                                          text=query).delete()
                s = Search(user=get_user_object(request), 
                           text=query, 
                           publication_date=dnow)
                s.save()

            if where == "statute":
                main_query = Section.search.query(query)

            if where == "title":
                main_query = Title.search.query(query)
                print main_query

            if where == "regulation":
                main_query = Regulation.search.query(query)

            if where == "irsruling":
                main_query = IRSRevenueRulings.search.query(query)

            if where == "irsprivateletter":
                main_query = IRSPrivateLetter.search.query(query)

            if where == "comment":
                main_query = Comment.search.query(query)

            if where == "post":
                main_query = Post.search.query(query)

            if where == "forms":
                main_query = FormAndInstruction.search.query(query)

            if where == "namedacts":
                main_query = NamedStatute.search.query(query)

            if where == "publications":
                main_query = Publication.search.query(query)

            if where == "decisions":
                main_query = Decision.search.query(query)

            if where == "iletters":
                main_query = InformationLetter.search.query(query)

            if where == "wdeterminations":
                main_query = WrittenDetermination.search.query(query)

            if where == "everywhere":
                if "/" in query:
                    mode = 'SPH_MATCH_ALL'
                else:
                    mode = 'SPH_MATCH_EXTENDED2'

                search = SphinxQuerySet(
                    index = ("uslaw_section uslaw_decision "
                             "uslaw_publications uslaw_popular_name "
                             "uslaw_title uslaw_forms "
                             "uslaw_title regulations uslaw_wdeterminations "
                             "post comment uslaw_iletters"),
                    weights = {
                        'title': 100,
                        'description': 60,
                        'add_field':10,
                        'text': 20,
                        },
                    mode = mode,
                    rankmode = 'SPH_RANK_BM25'#SPH_RANK_PROXIMITY
                    )
                main_query = search.query(query)

            #print "DATE sort %s" % date_sort
            if date_sort == 'asc':
                main_query = main_query.order_by('ext_date')
            elif date_sort == 'desc':
                main_query = main_query.order_by('-ext_date')
            
            """
            p_main = Paginator(main_query, 20)
            paginator = None
            paginator = p_main
            try:
                main_result = p_main.page(page_id)
            except EmptyPage:
                paginator = None
            else:
                page_obj = main_result
            page_range = get_page_range(paginator, page_id)
            """
            #p_main = Paginator(main_query, 20)
            paginator, page_obj, page_range, page_id = prepeare_pagination(main_query, request)


    else:
        searchform = SearchForm(initial={"page":"1"})
        searchform.fields['where'].widget = forms.Select( \
                          choices=SearchForm.SEARCH_CHOICES, 
                          attrs={"class":"right_btn", "style":""})

    return render(request, "search/search.html", locals())


def load_regulations(request):
    """Regulations ajah view"""
    try:
        section_id = int(request.GET.get('section', None))
    except ValueError:
        raise Http404

    section = get_object_or_404(Section, pk=section_id)
    rs = Regulation.objects.filter(Q(sections=section) \
                                   | Q(main_section =section)
                                   ).distinct().order_by("-rate", "section")
    return render(request, "laws/resources.html", {"section_id":section_id,
                                                   "section":section,
                                                   "rs":rs})

def load_rulings(request):
    """Rulings ajah view"""
    try:
        section_id = int(request.GET.get('section', None))
    except ValueError:
        raise Http404

    section = get_object_or_404(Section, pk=section_id)
    rs = IRSRevenueRulings.objects.filter( \
                        sections=section).order_by("-rate")
    return render(request, "laws/resources.html", {"section_id":section_id,
                                                   "section":section,
                                                   "rs":rs})


def view_regulation(request, section):
    """Regulation view"""
    active_section = 'browse'
    r = get_object_or_404(Regulation, section=section)
    searchform = SearchForm()
    user = get_user_object(request)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        pass
    object_ = r
    content_type = ContentType.objects.get_for_model(Regulation)
    comment_form = CommentForm(initial={'content_type':content_type})
    comments = Comment.objects.filter(content_type=content_type, 
                                      object_id=object_.id \
                                          ).order_by("publication_date")
    outdated = OutdatedResource.objects.filter(object_id=object_.id, 
                                               content_type__pk=content_type.id \
                                                   ).count()
    outdated_by_user = OutdatedResource.objects.filter(object_id=object_.id, 
                                                content_type__pk=content_type.id, 
                                                       user=user)
    if outdated == 0:
        outdated = False
    tags = TaggedItem.objects.filter(object_id=object_.id, 
                                     content_type__pk=content_type.id )
    tagsform = TaggedItemForm(initial={"next":r.get_absolute_url(), 
                                       "content_type":content_type.id, 
                                       "object_id":object_.id})
    return render(request, "laws/view_regulation.html", locals())

def view_ruling(request, section):
    """Ruling view"""
    active_section = 'browse'
    r = get_object_or_404(IRSRevenueRulings, section=section)
    searchform = SearchForm()
    user = get_user_object(request)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        object_type = ContentType.objects.get_for_model(Profile)
        #tags = TaggedItem.objects.filter(object_id=profile.id, 
                              #content_type__pk=object_type.id )
    object_ = r
    content_type = ContentType.objects.get_for_model(IRSRevenueRulings)
    comment_form = CommentForm(initial={'content_type':content_type})
    comments = Comment.objects.filter(content_type=content_type, 
                                      object_id=object_.id \
                                          ).order_by("publication_date")
    outdated = OutdatedResource.objects.filter(object_id=object_.id, 
                                             content_type__pk=content_type.id \
                                              ).count()
    outdated_by_user = OutdatedResource.objects.filter(object_id=object_.id, 
                                           content_type__pk=content_type.id, 
                                                       user=user)
    if outdated == 0:
        outdated = False
    tags = TaggedItem.objects.filter(object_id=object_.id, 
                                     content_type__pk=content_type.id )
    tagsform = TaggedItemForm(initial={"next":r.get_absolute_url(), 
                                       "content_type":content_type.id, 
                                       "object_id":object_.id})
    return render(request, "laws/view_ruling.html", locals())

def view_private_letter(request, irs_id):
    """Private letter view"""
    active_section = 'browse'
    r = get_object_or_404(IRSPrivateLetter, pk = irs_id)
    searchform = SearchForm()
    user = get_user_object(request)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        object_type = ContentType.objects.get_for_model(Profile)
        #tags = TaggedItem.objects.filter(object_id=profile.id, 
                                #content_type__pk=object_type.id )
    object_ = r
    content_type = ContentType.objects.get_for_model(IRSPrivateLetter)
    comment_form = CommentForm(initial={'content_type':content_type})
    comments = Comment.objects.filter(content_type=content_type, 
                              object_id=object_.id).order_by("publication_date")
    outdated = OutdatedResource.objects.filter(object_id=object_.id, 
                                  content_type__pk=content_type.id).count()
    if outdated == 0:
        outdated = False
    tags = TaggedItem.objects.filter(object_id=object_.id, 
                                     content_type__pk=content_type.id )
    tagsform = TaggedItemForm(initial={"next":r.get_absolute_url(), 
                                       "content_type":content_type.id, 
                                       "object_id":object_.id})
    return render(request, "laws/view_irsprivateletter.html", locals())
                 

def irs_private_letters(request):
    """IRS private letters"""
    active_section = 'browse'
    user = get_user_object(request)
    searchform = SearchForm()
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        pass
    irs = IRSPrivateLetter.objects.filter().order_by("section")
    paginator, page, page_range, page_id = prepeare_pagination(irs, request)
    return render(request, "laws/irs_private_letters.html", locals())

def preview_resource(request, r_id):
    """Resource preview"""
    r = get_object_or_404(Resource, pk=r_id)
    return render(request, "laws/preview_resource.html", {"r":r})

def vote(request, r_id, v):
    """Vote for resource"""
    r = get_object_or_404(Resource, pk=r_id)
    if v == "0":
        r.rate = r.rate - 1
        r.save()
    if v == "1":
        r.rate = r.rate + 1
        r.save()
    return render(request, "laws/vote.html", {"r":r, "v":v, "r_id":r_id})

def regulations(request):
    """View regulations list"""
    active_section = 'browse'
    searchform = SearchForm()
    user = get_user_object(request)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        avatar = False
    regulations = Regulation.objects.filter().order_by("order_1", "order_2", "order_3")
    paginator, page, page_range, page_id = prepeare_pagination(regulations, request)
    return render(request, "laws/regulations.html", locals())

def irsrulings(request):
    """IRS rulings list"""
    active_section = 'browse'
    user = get_user_object(request)
    searchform = SearchForm()
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        pass
   
    rulings = IRSRevenueRulings.objects.filter().order_by("section")
    paginator, page, page_range, page_id = prepeare_pagination(rulings, request)
    return render(request, "laws/irsrulings.html", locals())


def formsandinstructions(request):
    """View forms and instructions list"""
    active_section = 'browse'
    searchform = SearchForm()
    user = get_user_object(request)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        avatar = False
    forms = FormAndInstruction.objects.filter().order_by("-product_number")
    paginator, page, page_range, page_id = prepeare_pagination(forms, request)
    return render(request, "laws/formsandinstructions.html", locals())

def view_formsandinstructions(request, pk):
    active_section = 'browse'
    r = get_object_or_404(FormAndInstruction, pk=pk)
    searchform = SearchForm()
    user = get_user_object(request)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        object_type = ContentType.objects.get_for_model(Profile)
        #tags = TaggedItem.objects.filter(object_id=profile.id, 
                                #content_type__pk=object_type.id )
    object_ = r
    content_type = ContentType.objects.get_for_model(FormAndInstruction)
    comment_form = CommentForm(initial={'content_type':content_type })
    comments = Comment.objects.filter(content_type=content_type, 
                              object_id=object_.id).order_by("publication_date")
    outdated = OutdatedResource.objects.filter(object_id=object_.id, 
                                  content_type__pk=content_type.id).count()
    if outdated == 0:
        outdated = False
    tags = TaggedItem.objects.filter(object_id=object_.id, 
                                     content_type__pk=content_type.id )
    tagsform = TaggedItemForm(initial={"next": r.get_absolute_url(), 
                                       "content_type": content_type.id, 
                                       "object_id": object_.id})
    return render(request, "laws/view_formsandinstructions.html", locals())

def publications(request):
    """View publications list"""
    active_section = 'browse'
    searchform = SearchForm()
    user = get_user_object(request)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        avatar = False
    publications = Publication.objects.filter().order_by("-product_number")
    paginator, page, page_range, page_id = prepeare_pagination(publications, request)
    
    return render(request, "laws/publications.html", locals())

def view_publication(request, pk):
    """View Publication"""
    active_section = 'browse'
    r = get_object_or_404(Publication, pk=pk)
    searchform = SearchForm()
    user = get_user_object(request)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        object_type = ContentType.objects.get_for_model(Profile)
        #tags = TaggedItem.objects.filter(object_id=profile.id, 
                                #content_type__pk=object_type.id )
    object_ = r
    content_type = ContentType.objects.get_for_model(Publication)
    comment_form = CommentForm(initial={'content_type':content_type })
    comments = Comment.objects.filter(content_type=content_type, 
                              object_id=object_.id).order_by("publication_date")
    outdated = OutdatedResource.objects.filter(object_id=object_.id, 
                                  content_type__pk=content_type.id).count()
    if outdated == 0:
        outdated = False
    tags = TaggedItem.objects.filter(object_id=object_.id, 
                                     content_type__pk=content_type.id )
    tagsform = TaggedItemForm(initial={"next": r.get_absolute_url(), 
                                       "content_type": content_type.id, 
                                       "object_id": object_.id})
    return render(request, "laws/view_publication.html", locals())


def decisions(request):
    """View decisions list"""
    active_section = 'browse'
    searchform = SearchForm()
    user = get_user_object(request)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        avatar = False
    decisions = Decision.objects.filter().order_by("-product_number")
    paginator, page, page_range, page_id = prepeare_pagination(decisions, request)
    return render(request, "laws/decisions.html", locals())

def view_decision(request, pk):
    """View Decision"""
    active_section = 'browse'
    r = get_object_or_404(Decision, pk=pk)
    searchform = SearchForm()
    user = get_user_object(request)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        object_type = ContentType.objects.get_for_model(Profile)
        #tags = TaggedItem.objects.filter(object_id=profile.id, 
                                #content_type__pk=object_type.id )
    object_ = r
    content_type = ContentType.objects.get_for_model(Publication)
    comment_form = CommentForm(initial={'content_type':content_type })
    comments = Comment.objects.filter(content_type=content_type, 
                              object_id=object_.id).order_by("publication_date")
    outdated = OutdatedResource.objects.filter(object_id=object_.id, 
                                  content_type__pk=content_type.id).count()
    if outdated == 0:
        outdated = False
    tags = TaggedItem.objects.filter(object_id=object_.id, 
                                     content_type__pk=content_type.id )
    tagsform = TaggedItemForm(initial={"next": r.get_absolute_url(), 
                                       "content_type": content_type.id, 
                                       "object_id": object_.id})
    return render(request, "laws/view_decision.html", locals())


def iletters(request):
    """View information letters list"""
    active_section = 'browse'
    searchform = SearchForm()
    user = get_user_object(request)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        avatar = False
    letters = InformationLetter.objects.filter().order_by("-product_number")
    paginator, page, page_range, page_id = prepeare_pagination(letters, request)
    return render(request, "laws/iletters.html", locals())

def view_iletter(request, pk):
    """View Information Letter"""
    active_section = 'browse'
    r = get_object_or_404(InformationLetter, pk=pk)
    searchform = SearchForm()
    user = get_user_object(request)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        object_type = ContentType.objects.get_for_model(Profile)

    object_ = r
    content_type = ContentType.objects.get_for_model(Publication)
    comment_form = CommentForm(initial={'content_type':content_type })
    comments = Comment.objects.filter(content_type=content_type, 
                              object_id=object_.id).order_by("publication_date")
    outdated = OutdatedResource.objects.filter(object_id=object_.id, 
                                  content_type__pk=content_type.id).count()
    if outdated == 0:
        outdated = False
    tags = TaggedItem.objects.filter(object_id=object_.id, 
                                     content_type__pk=content_type.id )
    tagsform = TaggedItemForm(initial={"next": r.get_absolute_url(), 
                                       "content_type": content_type.id, 
                                       "object_id": object_.id})
    return render(request, "laws/view_iletter.html", locals())


def written_determinations(request):
    """View written determinations list"""
    active_section = 'browse'
    searchform = SearchForm()
    user = get_user_object(request)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        avatar = False
    wds = WrittenDetermination.objects.filter().order_by("-product_number")
    paginator, page, page_range, page_id = prepeare_pagination(wds, request)
    return render(request, "laws/written_determinations.html", locals())

def view_wdetermination(request, pk):
    """View Information Letter"""
    active_section = 'browse'
    r = get_object_or_404(WrittenDetermination, pk=pk)
    searchform = SearchForm()
    user = get_user_object(request)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        object_type = ContentType.objects.get_for_model(Profile)

    object_ = r
    content_type = ContentType.objects.get_for_model(Publication)
    comment_form = CommentForm(initial={'content_type':content_type })
    comments = Comment.objects.filter(content_type=content_type, 
                              object_id=object_.id).order_by("publication_date")
    outdated = OutdatedResource.objects.filter(object_id=object_.id, 
                                  content_type__pk=content_type.id).count()
    if outdated == 0:
        outdated = False
    tags = TaggedItem.objects.filter(object_id=object_.id, 
                                     content_type__pk=content_type.id )
    tagsform = TaggedItemForm(initial={"next": r.get_absolute_url(), 
                                       "content_type": content_type.id, 
                                       "object_id": object_.id})
    return render(request, "laws/view_written_determination.html", locals())


def most_referenced(request):
    """Draw tags cloud of the most referenced sections in Title 26 """
    user = get_user_object(request)
    if user:
        profile = get_profile_object(user)
    active_section = "tools"
    cursor = connection.cursor()
#    cursor.execute("""select a.section, co / 15, a.header as header 
#       from laws_section a, (
#       select count(*) as co, a.id 
#       	      from laws_section a, reference_sections b 
#              where a.id=b.to_section_id 
#              group by a.id 
#   	      order by count(*) desc) b 
#       where a.id=b.id; """)

    cursor.execute("""select id 
                        from laws_title 
                       where title='26' 
                         and parent_id is null;""") #  Get Title 26 id
    rows = cursor.fetchmany(size=1)
    top_title_id = rows[0][0]
    cursor.execute("""select e.id, e.section, e.header, f.co from
                   (select a.to_section_id as sid, count(a.*) / 2 as co 
                         from (select b.id as from_section_id, 
                                      c.section_id as to_section_id
                                 from laws_section_reference_subsection c, 
                                      laws_section b, laws_subsection d 
                                where c.section_id=b.id 
                                  and d.id=c.subsection_id
                                  and b.top_title_id=%s
                            union all select from_section_id, to_section_id
                                        from laws_section_reference_section) a
                        group by a.to_section_id 
                        order by count(a.*) desc 
                        limit 2500) f, laws_section e
                      where f.sid = e.id 
                        and e.top_title_id=%s
                   order by f.co desc; """ % (top_title_id, top_title_id))
    rows = cursor.fetchmany(size=500)
    if not request.GET.has_key('sort'):
        random.shuffle(rows)
    return render(request, "laws/most_referenced.html", locals())

def my404(request):
    """We need this handler to populate some variables for flatpages """
    user = get_user_object(request)
    profile = get_profile_object(user)
    response = render_to_response('404.html', locals(), 
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response

def tax_map(request):
    """ Draw taxmap"""
    active_section = "tools"
    #sections = Section.objects.filter()[:1]
    form = SectionsForm(initial={'link_type':'map',}) 
    #display_bubble = False
    #link_type = "map"
    return render(request, "laws/tax_map.html",
                  {"active_section":active_section,
                   "form":form})


def tax_map_ajax(request):
    """Draw ajax taxmap. 
    We use raw SQL because django ORM generate
    thousands queries"""
    if request.method == 'GET':
        form = SectionsForm(request.GET)
        if form.is_valid():
            content_type = ContentType.objects.get_for_model(Section)
            #print content_type.id
            sections = form.cleaned_data['sections']
            cursor = connection.cursor()
            back_ref = []
            back_subref = []
            display_selected_sections = form.cleaned_data['display_selected_sections']
            #print display_selected_sections
            if display_selected_sections:
                sections_ids = [str(s.id) for s in sections]
                query = """select distinct a.id, b.to_section_id, 
                                           a.section, a.header
                   from laws_section_reference_section b, 
                        laws_section a, laws_title t 
                  where to_section_id in (%s)  
                    and a.id=b.from_section_id 
                    and b.from_section_id in (%s) 
                    and a.top_title_id = t.id 
                    and t.title='26';
                   """ % (",".join(sections_ids), ",".join(sections_ids))
                #print query
                cursor.execute(query)

                back_refs = cursor.fetchall()
                back_ref = back_ref + back_refs
                query = """
                  select distinct b.id, a.section_id, b.section, b.header
                    from "laws_subsection" a, "laws_section" b, "laws_section_reference_subsection" c, laws_title t
                   where b.id = c.section_id AND
                         c.subsection_id = a.id AND
                         c.section_id in (%s) AND
                         a.section_id in (%s)
                        and b.top_title_id = t.id 
                        and t.title='26';
                   """ % (",".join(sections_ids), ",".join(sections_ids),)
                #print query
                cursor.execute(query)

                back_subrefs = cursor.fetchall()
                back_subref = back_subref + back_subrefs
                if form.cleaned_data['display_avatars']:
                    ids = sections_ids
                    for r in back_subref:
                        ids.append(str(r[0]))
                    for r in back_ref:
                        ids.append(str(r[0]))
                    ids = list(set(ids))
                    query = """select object_id, count(*), max(e.picter) 
                                 from "comment_comment" d, "users_profile" e 
                                where object_id in (%s)  
                                  and content_type_id = %s 
                                  and d.profile_id=e.id 
                             group by object_id, e.id;""" % \
                                  (",".join(ids), content_type.id)
                    cursor.execute(query)

                    profiles = cursor.fetchall()

            else:
                for section in sections:
                    cursor.execute("""select distinct a.id, b.to_section_id, 
                                                      a.section,  a.header
                       from laws_section_reference_section b, 
                            laws_section a, "laws_title" t
                       where to_section_id=%s and a.id=b.from_section_id
                       and a.top_title_id = t.id 
                       and t.title='26';
                       """%section.id)

                    back_refs = cursor.fetchall()
                    back_ref = back_ref + back_refs

                    cursor.execute("""
                      select distinct b.id, a.section_id, b.section, b.header
                        from "laws_subsection" a, 
                             "laws_section" b, 
                             "laws_section_reference_subsection" c, 
                             "laws_title" t
                       where b.id = c.section_id AND
                             c.subsection_id = a.id AND
                             a.section_id=%s
                             and b.top_title_id = t.id 
                             and t.title='26';
                       """%section.id)

                    back_subrefs = cursor.fetchall()
                    back_subref = back_subref + back_subrefs
                    if form.cleaned_data['display_avatars']:
                        ids = [str(section.id),]
                        for r in back_subref:
                            ids.append(str(r[0]))
                        for r in back_ref:
                            ids.append(str(r[0]))
                        ids = list(set(ids))
                        query = """select object_id, count(*), max(e.picter) 
                                     from "comment_comment" d, "users_profile" e 
                                    where object_id in (%s)  
                                      and content_type_id = %s 
                                      and d.profile_id=e.id 
                                 group by object_id, e.id;""" % \
                                      (",".join(ids), content_type.id)
                        cursor.execute(query)

                        profiles = cursor.fetchall()


            display_bubble = form.cleaned_data['display_bubble']
            link_type = form.cleaned_data['link_type'] 
            #print link_type
            if display_selected_sections and \
               len(back_subref) == 0 and len(back_ref) == 0:
                no_sections = True
            return render(request, "laws/tax_map_ajax.html", locals())

        else:
            errors = form.errors
    return render(request, "laws/tax_map_ajax.html", locals())

def goto_section(request):
    """Redirect to section"""
    if request.method == "POST":
        sec = request.POST.get("section_id", False)
        title = request.POST.get("top_title_id", False)
        if sec and title:
            if "usc" in sec.lower():
                sec = sec.lower()
                t = sec.split("usc")
                try:
                    new_title = int(t[0].strip())
                except ValueError:
                    return HttpResponseRedirect("/laws/search/")
                new_sec = t[1].strip()
                try:
                    tt = Title.objects.get(title=new_title)
                except Title.DoesNotExist:
                    tt = Title.objects.get(pk = title)
                try:
                    ss = Section.objects.get(top_title = tt, 
                                             section = new_sec)
                except Section.DoesNotExist:
                    return HttpResponseRedirect("/laws/search/")
            else:
                tt = Title.objects.get(pk = int(title.strip()))
                try:
                    ss = Section.objects.get(top_title = tt, 
                                             section = sec.strip())
                except Section.DoesNotExist:
                    return HttpResponseRedirect("/laws/search/")
                except Section.MultipleObjectsReturned:
                    url = reverse("multiple_sections_page", 
                                  kwargs={'title':str(title.strip()), 
                                          'section':sec.strip()})
                    return HttpResponseRedirect(url)
        return HttpResponseRedirect(ss.get_absolute_url())
    else:
        raise Http404

def view_publaw(request, publaw):
    """Public Law view"""
    pl = get_object_or_404(PubLaw, pk=publaw)
    object_ = pl
    active_section = 'browse'
    form = CommentForm()
    searchform = SearchForm()
    user = get_user_object(request)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        pass
    content_type = ContentType.objects.get_for_model(pl)
    comment_form = CommentForm(initial={'content_type':content_type})
    comments = Comment.objects.filter(content_type=content_type, 
                                      object_id=object_.id \
                                      ).order_by("publication_date")
    tags = TaggedItem.objects.filter(object_id=object_.id, 
                                     content_type__pk=content_type.id )
    outdated = OutdatedResource.objects.filter(object_id=object_.id, 
                               content_type__pk=content_type.id).count()
    outdated_by_user = OutdatedResource.objects.filter(object_id=object_.id, 
                                             content_type__pk=content_type.id, 
                                             user=user)
    if outdated == 0:
        outdated = False
    tagsform = TaggedItemForm(initial={"next":object_.get_absolute_url(), 
                                       "content_type":content_type.id, 
                                       "object_id":object_.id})
    return render(request, "laws/publaw.html", locals())

def load_subtitles(request):
    """Load subtitles (ajah)"""
    pk = request.GET.get("pk", 0)
    titles = Title.objects.filter(parent=pk)
    sections = Section.objects.filter(title__id=pk)
    return render(request, "laws/titles-list.html", {"pk":pk, "titles":titles,
                                                     "sections":sections})

def multiple_sections(request, title, section):
    title = get_object_or_404(Title, title=title, parent=None)
    sections = Section.objects.filter(section=section, top_title=title)
    if len(sections) < 2:
        raise Http404
    return render(request, "laws/mutliple-sections.html", {"title":title,
                                                           "sections":sections})

def view_named_act(request, pk):

    active_section = 'browse'
    r = get_object_or_404(NamedStatute, pk=pk)
    searchform = SearchForm()
    user = get_user_object(request)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        object_type = ContentType.objects.get_for_model(Profile)
        #tags = TaggedItem.objects.filter(object_id=profile.id, 
                                #content_type__pk=object_type.id )
    object_ = r
    content_type = ContentType.objects.get_for_model(FormAndInstruction)
    comment_form = CommentForm(initial={'content_type':content_type })
    comments = Comment.objects.filter(content_type=content_type, 
                              object_id=object_.id).order_by("publication_date")
    outdated = OutdatedResource.objects.filter(object_id=object_.id, 
                                  content_type__pk=content_type.id).count()
    if outdated == 0:
        outdated = False

    tags = TaggedItem.objects.filter(object_id=object_.id, 
                                     content_type__pk=content_type.id )
    tagsform = TaggedItemForm(initial={"next":r.get_absolute_url(), 
                                       "content_type":content_type.id, 
                                       "object_id":object_.id})

    return render(request, "laws/view_named_act.html", locals())


def named_acts(request):
    """Named Acts list"""
    active_section = 'browse'
    user = get_user_object(request)
    searchform = SearchForm()
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        pass
  
    ns = NamedStatute.objects.filter().order_by("title")
    paginator, page, page_range, page_id = prepeare_pagination(ns, request)
    return render(request, "laws/named-acts.html", locals())

def internal_revenue_manual_toc(request):
    """TOC for IRM"""
    active_section = 'browse'
    user = get_user_object(request)
    searchform = SearchForm()
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        pass
    irms = InternalRevenueManualToc.objects.filter(level=0).order_by("order_id")
    return render(request, "laws/irm-toc.html", locals())

def internal_revenue_manual_toc_ajax(request):
    """TOC for IRM (ajax version)"""
    try:
        top_irm = int(request.GET.get('pk', ''))
    except ValueError:
        raise Http404
    irms = InternalRevenueManualToc.objects.filter(parent__pk=top_irm).order_by("order_id")
    return render(request, "laws/irm-list.html", locals())

def irm_item(request, item_id):
    """IRM"""
    active_section = 'browse'
    user = get_user_object(request)
    searchform = SearchForm()
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        pass
    irm_toc = get_object_or_404(InternalRevenueManualToc, pk=item_id)
    if irm_toc.level < 2:
        irms = InternalRevenueManualToc.objects.filter(parent=irm_toc).order_by("order_id")
        return render(request, "laws/irm-toc.html", locals())
    else:
        r = InternalRevenueManual.objects.get(toc=irm_toc)
        return render(request, "laws/view_irm.html", locals())



def internal_revenue_bulletin_toc(request):
    """TOC for IRB"""
    active_section = 'browse'
    user = get_user_object(request)
    searchform = SearchForm()
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        pass
    irbs = InternalRevenueBulletinToc.objects.filter(level=0).exclude(name__exact='').order_by("-current_through")
    return render(request, "laws/irb-toc.html", locals())

def internal_revenue_bulletin_toc_ajax(request):
    """TOC for IRB (ajax version)"""
    try:
        top_irb = int(request.GET.get('pk', ''))
    except ValueError:
        raise Http404
    irbs = InternalRevenueBulletinToc.objects.filter(parent__pk=top_irb).exclude(name__exact='').order_by("order_id")
    return render(request, "laws/irb-list.html", locals())

def irb_item(request, item_id):
    """IRB"""
    print item_id
    active_section = 'browse'
    user = get_user_object(request)
    searchform = SearchForm()
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        pass
    irb_toc = get_object_or_404(InternalRevenueBulletinToc, pk=item_id)
    print "Level", irb_toc.level
    if irb_toc.level < 2:
        irbs = InternalRevenueBulletinToc.objects.filter(parent=irb_toc).exclude(name__exact='').order_by("order_id")
        return render(request, "laws/irb-toc.html", locals())
    else:
        irbs = InternalRevenueBulletin.objects.filter(toc=irb_toc).order_by('part_id')
        
        tocs = InternalRevenueBulletinToc.objects.filter(parent=irb_toc).exclude(name__exact='').order_by('order_id')
        print len(irbs)
        return render(request, "laws/view_irb.html", locals())
