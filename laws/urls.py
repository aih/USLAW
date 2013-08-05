# -*- coding: utf-8 -*-
# TODO: make refactoring for urls module

from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    url(r'title-text-ajax/(?P<title_id>\d+)/',
        'laws.views.title_text_ajax', name="title_text"),
    url('^topics?/$', 'laws.views.topics', name='laws_topics'),
    url('^load_topic/$', 'laws.views.load_topic', name='load_topic'),
    url('^tax-map/$', 'laws.views.tax_map' , name="tax_map"),
    url('^tax-map-ajax/$', 'laws.views.tax_map_ajax' , name="tax_map_ajax"),
#    url('^save/(\d+)/$', 'laws.views.save_document', name='save_document'),
#    url('^delete/(\d+)/$', 'laws.views.delete_document', name='delete_document'),
#    url('^ajah_search/?$', 'laws.views.ajah_search', name='laws_ajah_search'),

    url('^load_regulations/', 'laws.views.load_regulations',
        name="load_regulations"),
    url('^load_rulings/', 'laws.views.load_rulings',
        name="load_rulings"),
    url('^preview/(\d+)/$', 'laws.views.preview_section',
        name="preview_section"),
    url('^most_referenced/$','laws.views.most_referenced',
        name="most_referenced"),

    url('^regulations/$', 'laws.views.regulations',
        name="regulations"),
    url('^regulation/(.*)/', 'laws.views.view_regulation',
        name="view_regulation"),
    url('^irsrulings/$', 'laws.views.irsrulings',
        name="irsrulings"),
    url('^ruling/(.*)/', 'laws.views.view_ruling', name="view_ruling"),

    url('^named-acts/$', 'laws.views.named_acts',
        name="named_acts"),
    url('^named-acts/view/(?P<pk>\d+)/$', 'laws.views.view_named_act',
        name="view_named_act"),

    url('^forms-and-instructions/$', 'laws.views.formsandinstructions',
        name="formsandinstructions"),
    url('^fai/(\d+)/$', 'laws.views.view_formsandinstructions',
        name="view_formsandinstructions"),

    url('^publications/$', 'laws.views.publications',
        name="publications"),
    url('^publication/(\d+)/$', 'laws.views.view_publication',
        name="view_publication"),

    url('^actions-on-decisions/$', 'laws.views.decisions',
        name="decisions"),
    url('^aod/(\d+)/$', 'laws.views.view_decision',
        name="view_decision"),

    url('^information-letters/$', 'laws.views.iletters',
        name="iletters"),
    url('^information-letter/(\d+)/', 'laws.views.view_iletter',
        name="view_iletter"),

    url('^irsprivateletters/$', 'laws.views.irs_private_letters',
        name="irs_private_letters"),
    url('^irsprivateletter/(\d+)/$', 'laws.views.view_private_letter',
        name="view_irs_private_letter"),

    url('^written-determinations/$', 'laws.views.written_determinations',
        name="written_determinations"),
    url('^wd/(\d+)/$', 'laws.views.view_wdetermination',
        name="view_written_determination"),

    url('^internal-revenue-manual-toc/$', 'laws.views.internal_revenue_manual_toc',
        name="irm_toc"),

    url('^load-internal-revenue-manual-toc/$', 'laws.views.internal_revenue_manual_toc_ajax',
        name="load_irm_toc"),

    url('^irm/(?P<item_id>\d+)/$', 'laws.views.irm_item',
        name="irm_item"),

    url('^previewresource/(\d+)/', 'laws.views.preview_resource',
        name="preview_resource"),

    url('^vote/(\d+)/(\d{1})/', 'laws.views.vote', name="vote"),

    url('^search/', 'laws.views.search', name='laws_search'),
    url('^target/(?P<target>.+)/$', 'laws.views.target', name='laws_target'),
#    url('^hoverbubble/$', 'laws.views.hoverbubble', name='laws_hoverbubble'), # new version of target
    url('^pub-laws/(?P<publaw>\d+)/$', 'laws.views.view_publaw',
        name='view_publaw'), 

    url('^print/(?P<section_url>(.*?))/(?P<section_id>(\d+))/(?P<psection>\w+)?$',
        'laws.views.print_it', name='print_section'),

    url('^(?P<title_url>([\-\w]+))/id-(?P<title_id>\d+)/$',
        'laws.views.title_index', name="title_index"),

    url('^title-(?P<title>([\-\w]+))/section-(?P<section>([\w\-\s]+))/id-(?P<section_id>(\d+))/$',
        'laws.views.section', name='laws_section'),
    url('^goto-section/$', 'laws.views.goto_section',
        name='goto_section'),
    url('^section/(.*?)/(\d+)/$', 'laws.views.section_redirect_map',
        name='laws_section_redirect_map'),

    url('^(?P<title>(\w+))/(?P<section>(.*?))/$', 'laws.views.section_redirect',
        name='laws_section_redirect'),

    url('^(?P<title>(\w+))/$', 'laws.views.title_redirect',
        name='laws_title_redirect'),

    url('^/?$', 'laws.views.index', name='laws_index'),
    url('^load_subtitles?$', 'laws.views.load_subtitles',
        name='load_subtitles'),
    url('select-section/(?P<title>\w+)/(?P<section>.*?)/$', 'laws.views.multiple_sections',
        name="multiple_sections_page"),
)
