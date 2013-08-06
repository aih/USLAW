#Laws FORMS                                           #

from django import forms

from laws.models import Section

class MyModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        if hasattr(obj, 'parent'):
            if obj.parent is None:
                l = u"%s USC %s" % (" ", obj.header[:65])
            else:
                l = u"%s USC %s" % (obj.title, obj.header[:65])
        else:
            l = u"%s" % (obj.header[:65])
        return l[:90]

#class MyModelChoiceField(forms.ModelChoiceField):
#    def label_from_instance(self, obj):
#        return u"%s USC %s" % (obj.title, obj.header[:75])

class SectionsForm(forms.Form):
    LINK_TYPE_CHOICES = (
        ('map', 'Links open map'),
        ('statutes', 'Links open statutes section'),
        
        )# MyModelMultiple
#    sections = MyModelMultipleChoiceField(queryset=Section.objects.filter(top_title__title='26').order_by('int_section'),  widget=forms.SelectMultiple(attrs={'width':'800px', 'size':'6', 'overflow':'hidden'}))
    sections = MyModelMultipleChoiceField(queryset=Section.objects.filter(top_title__title="26").order_by('int_section'), widget=forms.SelectMultiple(attrs={'width':'800px', 'size':'6', 'overflow':'hidden'}))
#    sections = forms.ModelMultipleChoiceField(queryset=Section.objects.filter(title__title='26').order_by('int_section'),  widget=forms.SelectMultiple(attrs={'width':'800px', 'size':'6', 'overflow':'hidden'}))
    link_type = forms.CharField(widget=forms.Select(choices=LINK_TYPE_CHOICES, attrs={'onchange':'$("#id_tax_map_form").submit();',}))
    display_bubble = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'onchange':'$("#id_tax_map_form").submit();',}))
    display_selected_sections = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'onchange':'$("#id_tax_map_form").submit();',}))
    display_avatars = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'onchange':'$("#id_tax_map_form").submit();',}))

class SearchForm(forms.Form):
    SEARCH_CHOICES = (
        ('everywhere', 'Everywhere'),
        ('statute', 'Statutes'),
        ('regulation', 'Regulations'),
        ('irsruling', 'IRS Revenue Rulings'),
        #('irsprivateletter','Private Letter Rulings'),
        ('title','Titles'),
        ('forms','Forms And Instructions'),
        ('publications','Publications'),
        ('decisions','Actions on Decisions'),
        ('iletters','Information Letters'),
        ('wdeterminations','Written Determinations'),
        ('namedacts','Named Acts'),
        ('comment', 'Comments'),
        ('post','News / Questions'),
    )

    DATE_SORT_CHOICES = (
        ('none', 'None'),
        ('asc', 'Ascending'),
        ('desc', 'Descending'),
    )
    query = forms.CharField(max_length=100, widget=forms.TextInput(\
        attrs={"class":"right_btn", "title":"Query",
               "onfocus":("$('#id_query').css('background','none'); ")
               ("var q=$('#id_query').val(); if (q=='Search...') ")
               ("{$('#id_query').val(''); $('#id_query').css('font-weight','bolder');}"),
               "onblur": ("var q=$('#id_query').val(); \r\n if (q=='') ")
               ("{$('#id_query').val('Search...'); $('#id_query').")
               ("css('font-weight','normal'); $('#id_query').css('background',")
               (" 'transparent url(/static/img/icons/magnifier.png)")
               (" no-repeat scroll right center'); } ")
               }), initial="Search...", label="Search...")
    where = forms.CharField(widget=forms.Select(choices=SEARCH_CHOICES,
                                                attrs={"class":"right_btn",
                                                       "style":"width:145px;",
                                                       "title":"Where"}, label="Where"),
                            required=False)
    p = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    date_sort = forms.CharField(max_length=20, widget=forms.HiddenInput(),
                                required=False)
