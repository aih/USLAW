# -*- coding: utf-8 -*-
"""Uslaw laws models"""
 
import sys
from datetime import datetime
from string import ascii_uppercase as ABC
from djangosphinx.models import SphinxSearch
import hashlib

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db import IntegrityError
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse

def str2int(text):
    """Helper for intelligetn sorting"""
    add = 0
    res = ""
    for c in text:
        if c.isdigit():
            res = "%s%s" % (res, c)
        else:
            try:
                add += ABC.index(c.upper()) + 1
            except ValueError:
                pass
    return int(res)*3 + add

def int_to_roman(input):
    """
    Convert an integer to Roman numerals.

    Examples:
    >>> int_to_roman(0)
    Traceback (most recent call last):
    ValueError: Argument must be between 1 and 3999

    >>> int_to_roman(-1)
    Traceback (most recent call last):
    ValueError: Argument must be between 1 and 3999

    >>> int_to_roman(1.5)
    Traceback (most recent call last):
    TypeError: expected integer, got <type 'float'>

    >>> for i in range(1, 21): print int_to_roman(i)
    ...
    I
    II
    III
    IV
    V
    VI
    VII
    VIII
    IX
    X
    XI
    XII
    XIII
    XIV
    XV
    XVI
    XVII
    XVIII
    XIX
    XX
    >>> print int_to_roman(2000)
    MM
    >>> print int_to_roman(1999)
    MCMXCIX
    """
    if type(input) != type(1):
        raise TypeError, "expected integer, got %s" % type(input)
    if not 0 < input < 4000:
        raise ValueError, "Argument must be between 1 and 3999"   

    ints = (1000, 900,  500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1)
    nums = ('M',  'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 
            'IX', 'V', 'IV', 'I')
    result = ""
    for i in range(len(ints)):
        count = int(input / ints[i])
        result += nums[i] * count
        input -= ints[i] * count
    return result

def roman_to_int(input):
    """Convert a roman numeral to an integer.
    
    >>> r = range(1, 4000)
    >>> nums = [int_to_roman(i) for i in r]
    >>> ints = [roman_to_int(n) for n in nums]
    >>> print r == ints
    1

    >>> roman_to_int('VVVIV')
    Traceback (most recent call last):
    ...
    ValueError: input is not a valid roman numeral: VVVIV
    >>> roman_to_int(1)
    Traceback (most recent call last):
    ...
    TypeError: expected string, got <type 'int'>
    >>> roman_to_int('a')
    Traceback (most recent call last):
    ...
    ValueError: input is not a valid roman numeral: A
    >>> roman_to_int('IL')
    Traceback (most recent call last):
    ...
    ValueError: input is not a valid roman numeral: IL
    """
    if type(input) != type(""):
        raise TypeError, "expected string, got %s" % type(input)
    input = input.upper().replace('-','')
    nums = ['M', 'D', 'C', 'L', 'X', 'V', 'I']
    ints = [1000, 500, 100, 50,  10,  5,   1]
    places = []
    for c in input:
        if not c in nums:
            raise ValueError, "input is not a valid roman numeral: %s" % input
    for i in range(len(input)):
        c = input[i]
        value = ints[nums.index(c)]
        # If the next place holds a larger number, this value is negative.
        try:
            nextvalue = ints[nums.index(input[i +1])]
            if nextvalue > value:
                value *= -1
        except IndexError:
            # there is no next place.
            pass
        places.append(value)
    sum = 0
    for n in places: sum += n
    # Easiest test for validity...
    if int_to_roman(sum) == input:
        return sum
    else:
        raise ValueError, 'input is not a valid roman numeral: %s' % input

class TextStore(models.Model):
    """
    We use this model for store big texts
    and optimisations.
    For inscreasing access for other tables 
    all texts stored in this model
    """
    text = models.TextField(null=True, blank=True)

class Title(models.Model):
    """Top level of Statutes tree. """

    search = SphinxSearch('uslaw_title')
    title = models.CharField(max_length=50, blank=True, default="")
    name = models.CharField(max_length=255, blank=True, default="")
    url = models.CharField(max_length=255, blank=True, null=True)
    parent = models.ForeignKey('self', related_name="parent_title", null=True, blank=True)
    int_title = models.IntegerField(default=0, editable=False) # we need this only for sorting
    debug = models.CharField(max_length=100, null=True, blank=True)
    text = models.TextField(null=True, blank=True)

    def get_ext_date(self):
        """Return external publication date"""
        return False

    def get_name(self):
        """Get name for template"""
        return self._meta.verbose_name_plural

    def save(self, *args, **kwargs):
        """Sorting
        there 4 ways to sort titles (examples):
        1. title = i (where i - integer).
        2. name = CHAPTER 1 - NORMAL TAXES AND SURTAXES
        3. name = Part B - Native Hawaiian Program (sort by letters)
        4. name = PART II - CRIMINAL PROCEDURE (Roman numerals)

        Also we need to handle titles with numbers+letters, like Title 26A. for that case we add 1 for such titles, other titles we *2
        """
        #self.name = self.name.replace('&mdash;', ' - ')
        int_title = ""
        add = 0
        debug = ""
        if self.title == "":
            titles = self.name.replace(u"—", " ").split(" ")
            if len(titles)>1: # assume second part is index
                try:
                    for c in titles[1]:
                        if c.isdigit():
                            int_title = int_title+c
                        else:
                            try:
                                add += ABC.index(c.upper()) + 1
                                debug = debug + "Add %s, c=%s" % (add, c)
                            except ValueError:
                                pass

                    if len(int_title)==0:
                        raise ValueError
                except ValueError:
                    debug = "Int convertion failed"
                    add = 0
                    try:
                        if "M" in titles[1] or "L" in titles[1] or "C" in titles[1] or "D" in titles[1]:
                            raise ValueError # this not roman numerals 
                        roman_t = titles[1].replace(".",'').split('-')
                        if len(roman_t)>1:
                            add = ABC.index(roman_t[1].upper()) + 1
                            int_title = str(roman_to_int(str(roman_t[0])))
                        else:
                            int_title = str(roman_to_int(str(titles[1])))
                        debug = str(roman_t)
                    except ValueError:
                        #print self.name, "ROMAN fails", roman_t
                        int_title = ""
                   
                        try:
                            for s in titles[1]:
                                int_title = str(ABC.index(s.upper())+1)
                        except ValueError:
                            debug = "all fails"
        else:
            for c in self.title:
                if c.isdigit():
                    int_title = int_title+c
                else:
                    add = ABC.index(c.upper()) + 1
        try:
            self.int_title = int(int_title)
        except ValueError:
            #print self.title, self.name
            #print int_title
            self.int_title = 0
        else:
            self.int_title = self.int_title * 2 + add
        self.url = slugify(self.name)
        #self.debug = debug[:100]
        super(Title, self).save(*args, **kwargs)    
        return 

    @models.permalink
    def get_absolute_url(self):
        return ("title_index", [self.url, self.id])

    @property
    def islast(self): 
        """return True if title have no childs"""
        c = Title.objects.filter(parent=self).count()
        if c == 0:
            return True
        else:
            return False
        
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('int_title', "name")
        verbose_name_plural = "US Code Titles"

class TmpSubsection(models.Model):
    """This model used for storing subsections before move them to Subsection model

    We need this because USC plugin can't indicate which subsection was changed,
    also order of the subsections can be changed.
    For solving this issue we save subsections to this temporary table and update
    Main Subsection model if something changed.
    """

    section = models.ForeignKey('Section')
    subsection = models.CharField(max_length=50, blank=True, default="")
    level = models.IntegerField(default=0)
    part_id = models.IntegerField(default=0)
    s_type = models.IntegerField(default=0)# 0 - regular, 1 - header , 2 - top Header
    text = models.TextField(null=True, blank=True)
    raw_text = models.TextField(null=True, blank=True)
    is_processed = models.BooleanField(default=False) #  Field for storing information about processed this field or no

    def __unicode__(self):
        return unicode(self.section)


class Subsection(models.Model):
    """Bottom level of Statutes tree.
    Note: If we have subsection!="" -> this is not full document, only part (subsection).
          If we have subsection =="" -> this is full document (section).
         FIXME: Maybe move subsections to another table?
    """
    #search = SphinxSearch() # optional: defaults to db_table
    # If your index name does not match MyModel._meta.db_table
    # Note: You can only generate automatic configurations from the ./manage.py script
    # if your index name matches.
    search = SphinxSearch('test1')
    objects = models.Manager()

    section = models.ForeignKey('Section')
    subsection = models.CharField(max_length=50, blank=True, default="")
    level = models.IntegerField(default=0)
    part_id = models.IntegerField(default=0)
    s_type = models.IntegerField(default=0)# 0 - regular, 1 - header , 2 - top Header
    text = models.TextField(null=True, blank=True)
    raw_text = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)  # file source
    hash = models.CharField(max_length=40, blank=True, default="")#, unique=True)
    is_active = models.BooleanField(default=True)
    is_outdated = models.BooleanField(default=False)
    is_processed = models.BooleanField(default=False) #  Field for storing information about processed this field or no

    
    def save_xml(self, *args, **kwargs):
        """This method called only from scripts."""
        if not self.hash:
            hh = unicode('%s-%s-%s-%s') % (self.section, self.subsection, self.text, self.level)
            #print hh
            hh = hh.encode('utf-8')
            self.hash = hashlib.sha224(hh).hexdigest()
            new = True
            if self.hash == "":
                print "Empty hash"
                sys.exit(2)

            s = Subsection.objects.filter(hash=self.hash).count()
            if s > 0:
                #print "old"
                return 

        else:
            new = False
            #print "#", 
        new = True
        #print "+",
        #print (u'TITLE: %s, SECTION: %s, SUBECTION: %s, PART_ID: %s, NEW: %s %s, level %s' % (
        #    self.section.title, self.section, self.subsection, self.part_id, 'YES' if new else 'NO', self.text, self.level))
        if len(self.text)>0:
            try:
                super(Subsection, self).save(*args, **kwargs)
            except IntegrityError, ex:
                doc = Subsection.objects.get(hash=self.hash)
                #import pdb; pdb.set_trace()

                print 'Existing doc: %s' % doc.description()
                print 'Current (failed) doc: %s' % self.description()
                raise

    @property
    def description(self):
        return 'TITLE: %s, SECTION: %s, SUBSECTION: %s, PART_ID: %s' % (
            self.title, self.section, self.subsection, self.part_id)

    #@models.permalink
    def get_absolute_url(self):
        url = "%s#%s" % (self.section.get_absolute_url(), self.id) #reverse("laws_section", args=(self.section.url, self.section.id))
        return url

    def get_print_url(self):
        url = reverse("print_section", args=(self.title, self.section))
        return url

    def __unicode__(self):
        return unicode(self.section) #.__unicode__()  #.title.title +u'§'+ self.section.section

    def set_name(self, psection_parts=None):
        self.name = unicode(self.title)
        if self.section:
            self.name += u"§%s" % self.section
            self.name += ''.join(psection_parts or [])

    class Meta:
        ordering = ('part_id',)


class Section(models.Model):
    search = SphinxSearch('uslaw_section')
    title = models.ForeignKey(Title)
    top_title = models.ForeignKey(Title, related_name="top_title", null=True, blank=True)
    section = models.CharField(max_length=100)
    header = models.CharField(max_length=512)
    int_section = models.IntegerField(default=0) # we need this only for sorting
    reference_title = models.ManyToManyField('Title', related_name='titles')
    reference_section = models.ManyToManyField('Section', related_name='sections')
    reference_subsection = models.ManyToManyField('Subsection', related_name='subsections')
    is_active = models.BooleanField(default=True)
    is_outdated = models.BooleanField(default=False)
    url = models.CharField(max_length=255, blank=True, null=True)
    section_text = models.TextField(null=True, blank=True)
    last_update = models.DateTimeField(blank=True, null=True)
    is_processed = models.BooleanField(default=False) #  Field for storing information about processed this field or no
    current_through = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=2046, null=True, blank=True)

    def __init__(self, *args, **kwargs):
        self.ABC_s = {}
        i = 0
        for k in ABC:
            self.ABC_s[k] = i
            i = i + 1

        super(Section, self).__init__(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('laws_section', (), {'title': str(self.top_title.title), 
                                     'section': self.section, 
                                     'section_id':self.id})

    def get_ext_date(self):
        """Return external publication date"""
        return self.current_through

    def get_name(self):
        """Get name for template"""
        return self._meta.verbose_name_plural

    def get_title(self):
        """Get top title object"""
        t = self.title
        while t.parent is not None:
            t = t.parent
        return t

    @models.permalink
    def get_print_url(self):
        return "laws.views.print_it", [self.url, self.id]

    def text(self):
        n = Subsection.objects.filter(section=self).order_by('subsection', 'level', 'part_id')
        if len(n) > 0:
            return n[0].text
        return None

    def save(self, *args, **kwargs):
        int_section = ""
        for c in self.section:
            if c.isdigit():
                int_section = int_section+c
                
        if len(int_section)>7:
            int_section = int_section[:6]
        try:
            self.int_section = int(int_section)
        except ValueError:
            self.int_section = 0
        #self.section = self.section.replace(u'–','-')
        self.url = slugify(self.header)[:255]
        super(Section, self).save(*args, **kwargs)    
        return 

    def get_next_url(self):
        try:
            n = int(self.section)
        except ValueError:
            try:
                s = ABC[self.ABC_s[self.section[-1:].upper()]+1]
            except KeyError:
                return False
            except:
                return False

            sec = self.section[:-1]+s
            n = Section.objects.filter(top_title=self.top_title, section=sec)
            if len(n)==0:
                try:
                    sec = int(self.section[:-1])-1                    
                except ValueError:
                    return False
                n = Section.objects.filter(top_title=self.top_title, 
                                           section=str(sec))
                if len(n) == 0:
                    n = False
        else:
            sec = str(self.section)+"A"
            n = Section.objects.filter(top_title=self.top_title, 
                                       section=str(sec))
            if len(n) == 0:
                sec = int(self.section)+1
                n = Section.objects.filter(top_title=self.top_title, 
                                           section=str(sec))
                if len(n) == 0:
                    for i in range(1, 20):
                        sec = int(self.section)+i
                        n = Section.objects.filter(top_title=self.top_title, 
                                                   section=str(sec))
                        if len(n) > 0:
                            break
                    if len(n) == 0:
                        n = False
        if n:
            #print n
            try:
                url = reverse("laws_section", args=(n[0].url, n[0].pk))
            except:
                url = False
            return url
        else:
            return False

    def get_previous_url(self):
        try:
            n = int(self.section)
        except ValueError:
            try:
                s = ABC[self.ABC_s[self.section[-1:].upper()]-1]                
            except KeyError:
                return False
            except:
                return False

            sec = self.section[:-1]+s
            n = Section.objects.filter(top_title=self.top_title, 
                                       section=sec)
            if len(n) == 0:
                try:
                    sec = int(self.section[:-1])-1                    
                except ValueError:
                    return False

                n = Section.objects.filter(top_title=self.top_title, 
                                           section=str(sec))
                if len(n) == 0:
                    n = False
        else:
            sec = int(self.section)-1
            n = Section.objects.filter(top_title=self.top_title, 
                                       section=str(sec))
            if len(n) == 0:
                for i in range(1, 20):
                    sec = int(self.section)-i
                    n = Section.objects.filter(top_title=self.top_title, 
                                               section=str(sec))
                    if len(n) > 0:
                        break
                if len(n) == 0:
                    n = False
        if n:
            try:
                url = reverse("laws_section", args=(n[0].url, n[0].pk))
            except:
                url = False
            return url
        else:
            return False

    def __unicode__(self):
        return u"%s → %s" % (self.top_title.title, self.header)

    class Meta:
        ordering = ('int_section', 'section')
        verbose_name_plural = "US Code Sections"

class TmpSectionAdditional(models.Model):
    """Tmp table for storing additional sections"""

    section = models.ForeignKey(Section)
    order = models.IntegerField(default=0)
    text = models.TextField()
    raw_text = models.TextField()
    publication_date = models.DateTimeField(default=datetime.now())
    sa_type = models.IntegerField(default=0)# 0 - regular text, 1 - Header
    is_processed = models.BooleanField(default=False) #  Field for storing information about processed this field or no

    def __unicode__(self):
        return "%s - %s" % (unicode(self.section), unicode(self.text[:20]))

class SectionAdditional(models.Model):
    """Additional informatio for section"""
    section = models.ForeignKey(Section)
    order = models.IntegerField(default=0)
    text = models.TextField()
    raw_text = models.TextField()
    publication_date = models.DateTimeField(default=datetime.now())
    sa_type = models.IntegerField(default=0)# 0 - regular text, 1 - Header
    is_processed = models.BooleanField(default=False) #  Field for storing information about processed this field or no

    def __unicode__(self):
        return "%s - %s" % (unicode(self.section), unicode(self.text[:20]))

    def sa_type_u(self): #
        "For api translate sa_type to text"
        if self.sa_type == 0:
            return "Regular text"
        else:
            return "Header"

class Regulation(models.Model):
    """Regulations.
    (2) Regulations, in the Code of Federal Regulations (CFR) are listed here [http://www.access.gpo.gov/cgi-bin/cfrassemble.cgi?title=201026]. 
    It is now available in bulk download in XML [http://www.gpo.gov/fdsys/bulkdata/CFR/2010/title-26] from here. 
    Data for previous years is here [http://www.gpo.gov/fdsys/bulkdata/CFR].

    Additional data from old years:
    http://www.access.gpo.gov/nara/cfr/waisidx_09/26cfrv7_09.html

    http://www.access.gpo.gov/nara/cfr/waisidx_09/26cfrv11_09.html
    """
    #search = SphinxSearch() # optional: defaults to db_table
    # If your index name does not match MyModel._meta.db_table
    # Note: You can only generate automatic configurations from the ./manage.py script
    # if your index name matches.
    search = SphinxSearch('regulations')
    section = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=500)
    document = models.FileField(blank=True, null=True, upload_to="uploads/documents/")
    main_section = models.ForeignKey(Section, null=True, blank=True, related_name="main_section")
    sections = models.ManyToManyField(Section)
    text = models.TextField(null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)
    shortlink = models.CharField(max_length=55, null=True, blank=True)
    browsable = models.BooleanField(default=True)
    rate = models.IntegerField(default=0)
    publication_date = models.DateTimeField(default=datetime.now())
    last_update = models.DateTimeField(blank=True, null=True)
    current_through = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_outdated = models.BooleanField(default=False)

    order_1 = models.IntegerField(default=0)
    order_2 = models.IntegerField(default=0)
    order_3 = models.IntegerField(default=0)

    external_publication_date = models.CharField(null=True, blank=True, max_length=20)
    
    def __unicode__(self):
        return u"§ %s %s" % (self.section, self.title)

    @models.permalink    
    def get_absolute_url(self):
        return ('laws.views.view_regulation', [str(self.section)])

    def get_ext_date(self):
        """Return external publication date"""
        return self.current_through

    def get_name(self):
        """Get name for template"""
        return self._meta.verbose_name_plural

    def save(self, *args, **kwargs):
        if self.id is not None:
            self.last_update = datetime.now()

        try:
            sections = self.section.split('.')
        except AttributeError:
            pass
        else:
            if len(sections) == 2:
                self.order_1 = str2int(sections[0])
                if "-" in sections[1]:
                    subsections = sections[1].split("-")
                    x1, x2 = str2int(subsections[0]), str2int(subsections[1])
                    self.order_2 = x1
                    self.order_3 = x2
                else:
                    self.order_2 = str2int(sections[1])
        super(Regulation, self).save(*args, **kwargs)    

    class Meta:
        verbose_name_plural = "Code of Federal Regulations"    
        
    
class IRSRevenueRulings(models.Model):
    """IRS revenue rulings
    (4) IRS rulings. The recent rulings are listed here [http://www.irs.gov/pub/irs-drop/], from rr-00-01.pdf to rr99-44.pdf). The most important ones are listed rr-2010-....

    """
    search = SphinxSearch() # optional: defaults to db_table
    # If your index name does not match MyModel._meta.db_table
    # Note: You can only generate automatic configurations from the ./manage.py script
    # if your index name matches.
    search = SphinxSearch('irsruling')
    section = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=500)
    document = models.FileField(blank=True, null=True, upload_to="uploads/documents/")
    sections = models.ManyToManyField(Section)
    text = models.TextField(null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)
    browsable = models.BooleanField(default=True)
    rate = models.IntegerField(default=0)
    publication_date = models.DateTimeField(default=datetime.now())
    is_active = models.BooleanField(default=True)
    is_outdated = models.BooleanField(default=False)
    current_through = models.DateField(null=True, blank=True)
    last_update = models.DateTimeField(blank=True, null=True)

    external_publication_date = models.CharField(null=True, blank=True, max_length=20)

    def __unicode__(self):
        return "%s" % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('laws.views.view_ruling', [str(self.section)])

    def get_ext_date(self):
        """Return external publication date"""
        return self.external_publication_date

    def get_name(self):
        """Get name for template"""
        return self._meta.verbose_name_plural


    class Meta:
        verbose_name_plural = "IRS Revenue Rulings"    

class IRSPrivateLetter(models.Model):
    """IRS Private Letter Rulings
    Source: http://www.irs.gov/pub/irs-wd/
    """
    search = SphinxSearch() # optional: defaults to db_table
    # If your index name does not match MyModel._meta.db_table
    # Note: You can only generate automatic configurations from the ./manage.py script
    # if your index name matches.
    search = SphinxSearch('irsprivateletter')
    section = models.CharField(max_length=100)
    title = models.CharField(max_length=500)
    document = models.FileField(blank=True, null=True, upload_to="uploads/documents/")
    sections = models.ManyToManyField(Section)
    text = models.TextField()
    link = models.CharField(max_length=255, null=True, blank=True)
    browsable = models.BooleanField(default=True)
    rate = models.IntegerField(default=0)
    letter_number = models.CharField(max_length=100, null=True, blank=True)
    letter_date = models.CharField(max_length=50, null=True, blank=True)
    
    publication_date = models.DateTimeField(default=datetime.now())
    is_active = models.BooleanField(default=True)
    is_outdated = models.BooleanField(default=False)
    current_through = models.DateField(null=True, blank=True)

    last_update = models.DateTimeField(blank=True, null=True)
    external_publication_date = models.CharField(null=True, blank=True, max_length=20)

    def __unicode__(self):
        return "%s" % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('laws.views.view_private_letter', [str(self.id)])

    def get_ext_date(self):
        """Return external publication date"""
        return self.external_publication_date

    def get_name(self):
        """Get name for template"""
        return self._meta.verbose_name_plural

    class Meta:
        verbose_name_plural = "IRS Private Letters Rulings"    


class PubLaw(models.Model):
    congress = models.CharField(max_length = 3)
    plnum = models.CharField(max_length = 10)
    billnum = models.CharField(max_length = 15) 
    text = models.TextField(null=True, blank=True)
    html = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return u"P.L. %s" % self.plnum

    @models.permalink
    def get_absolute_url(self):
        return ('laws.views.view_publaw', [str(self.id)])


class Classification(models.Model):
    pl = models.ForeignKey(PubLaw)
    section = models.ForeignKey(Section)
    plsection = models.CharField(max_length=20)
    sectionid = models.CharField(max_length=100, null=True, blank=True) # section HTML id as it appear in HTML

    def __unicode__(self):
        return u"%s %s" % (self.pl, self.section)

class UscodeHtml(models.Model):
    """
    Temporary table for store USCode html documents
    """
    url = models.CharField(max_length=500, unique=True)
    data = models.TextField()
    publication_date = models.DateTimeField(default=datetime.now())

    def __unicode__(self):
        return self.url

class USCTopic(models.Model):
    """
    US Code topics list
    """
    first_section = models.ForeignKey(Section,
                                      limit_choices_to={"top_title__title":"26",},
                                      related_name="first_section") # First section of the Topic
    last_section = models.ForeignKey(Section,
                                     limit_choices_to={"top_title__title":"26",},
                                     related_name="last_section")  # Last section of the Topic
    name = models.CharField(max_length=350, unique=True)
    order = models.IntegerField(default=0)

    class Meta:
        unique_together = ("first_section", "last_section")
    
    def __unicode__(self):
        return self.name


class FormAndInstruction(models.Model):
    """Forms and instructions from
    http://www.irs.gov/app/picklist/list/formsInstructions.html

    """
    #search = SphinxSearch() # optional: defaults to db_table
    search = SphinxSearch('uslaw_forms')
    product_number = models.CharField(max_length=50)
    title = models.CharField(max_length=500)
    document = models.FileField(blank=True, null=True, upload_to="uploads/documents/")
    sections = models.ManyToManyField(Section)
    text = models.TextField(null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)
    rate = models.IntegerField(default=0)

    publication_date = models.DateTimeField(default=datetime.now())
    is_active = models.BooleanField(default=True)
    is_outdated = models.BooleanField(default=False)
    revision_date = models.CharField(max_length=10)
    external_publication_date = models.DateTimeField(null=True, blank=True, max_length=20)
    last_update = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return "%s" % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('laws.views.view_formsandinstructions', [self.id])

    def get_ext_date(self):
        """Return external publication date"""
        return self.external_publication_date

    def get_name(self):
        return self._meta.verbose_name_plural

    class Meta:
        verbose_name_plural = "Forms and instructions"    


class NamedStatute(models.Model):
    """Popular names for Statute
    """
    #search = SphinxSearch() # optional: defaults to db_table
    search = SphinxSearch('uslaw_popular_name')
    title = models.CharField(max_length=300)
    description = models.CharField(max_length=1000)
    section = models.ForeignKey(Section, null=True, blank=True, limit_choices_to={"top_title__title":"26",})
    top_title = models.ForeignKey(Title, null=True, blank=True, limit_choices_to={"parent__isnull":True,})
    rate = models.IntegerField(default=0)
    publication_date = models.DateTimeField(default=datetime.now())
    is_active = models.BooleanField(default=True)
    is_outdated = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s" % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('view_named_act', (), {'pk':self.id})

    def get_ext_date(self):
        """Return external publication date"""
        return False

    def get_name(self):

        return self._meta.verbose_name_plural
    class Meta:
        verbose_name_plural = "Statutes Popular Names"    


class Publication(models.Model):
    """Publications from
    http://www.irs.gov/app/picklist/list/formsPublications.html

    """
    #search = SphinxSearch() # optional: defaults to db_table
    search = SphinxSearch('uslaw_publications')
    product_number = models.CharField(max_length=50)
    title = models.CharField(max_length=500)
    document = models.FileField(blank=True, null=True, upload_to="uploads/documents/")
    sections = models.ManyToManyField(Section)
    #text = models.TextField(null=True, blank=True)
    store = models.ForeignKey(TextStore, null=True, blank=True)

    link = models.CharField(max_length=255, null=True, blank=True)
    rate = models.IntegerField(default=0)

    publication_date = models.DateTimeField(default=datetime.now())
    is_active = models.BooleanField(default=True)
    is_outdated = models.BooleanField(default=False)
    revision_date = models.CharField(max_length=10)
    external_publication_date = models.DateField(null=True, blank=True, max_length=20)
    last_update = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return "%s" % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('laws.views.view_publication', [self.id])

    def get_ext_date(self):
        """Return external publication date"""
        return self.external_publication_date

    def get_name(self):
        return self._meta.verbose_name_plural

    class Meta:
        verbose_name_plural = "Publications"    


class Decision(models.Model):
    """Publications from
    http://www.irs.gov/app/picklist/list/actionsOnDecisions.html
    """
    #search = SphinxSearch() # optional: defaults to db_table
    search = SphinxSearch('uslaw_decision')
    product_number = models.CharField(max_length=50)
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=500)
    document = models.FileField(blank=True, null=True, upload_to="uploads/documents/")
    sections = models.ManyToManyField(Section)
    text = models.TextField(null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)
    rate = models.IntegerField(default=0)

    publication_date = models.DateTimeField(default=datetime.now())
    is_active = models.BooleanField(default=True)
    is_outdated = models.BooleanField(default=False)
    external_publication_date = models.DateField(null=True, blank=True, max_length=20)
    last_update = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return "%s" % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('laws.views.view_decision', [self.id])

    def get_ext_date(self):
        """Return external publication date"""
        return self.external_publication_date

    def get_name(self):
        return self._meta.verbose_name_plural

    class Meta:
        verbose_name_plural = "Actions on Decisions"    

class InformationLetter(models.Model):
    """Information Letters from
    http://www.irs.gov/app/picklist/list/informationLetters.html
    """
    #search = SphinxSearch() # optional: defaults to db_table
    search = SphinxSearch('uslaw_iletters')
    product_number = models.CharField(max_length=60)
    uilc = models.CharField(max_length=100)  #  UILC
    title = models.CharField(max_length=500)
    document = models.FileField(blank=True, null=True, upload_to="uploads/documents/")
    sections = models.ManyToManyField(Section)
    text = models.TextField(null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)
    rate = models.IntegerField(default=0)

    publication_date = models.DateTimeField(default=datetime.now())
    is_active = models.BooleanField(default=True)
    is_outdated = models.BooleanField(default=False)
    external_publication_date = models.DateField(null=True, blank=True, max_length=20)
    last_update = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return "%s - %s" % (self.product_number, self.title)

    @models.permalink
    def get_absolute_url(self):
        return ('laws.views.view_iletter', [self.id])

    def get_ext_date(self):
        """Return external publication date"""
        return self.external_publication_date

    def get_name(self):
        return self._meta.verbose_name_plural

    class Meta:
        verbose_name_plural = "Information Letters"    


class WrittenDetermination(models.Model):
    """Written Determinations from 
    http://www.irs.gov/app/picklist/list/writtenDeterminations.html
    """
    #search = SphinxSearch() # optional: defaults to db_table
    search = SphinxSearch('uslaw_wdeterminations')
    product_number = models.CharField(max_length=60)
    uilc = models.CharField(max_length=100)  #  UILC
    title = models.CharField(max_length=500)
    document = models.FileField(blank=True, null=True, upload_to="uploads/documents/")
    sections = models.ManyToManyField(Section)
    store = models.ForeignKey(TextStore, null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)
    rate = models.IntegerField(default=0)

    publication_date = models.DateTimeField(default=datetime.now())
    is_active = models.BooleanField(default=True)
    is_outdated = models.BooleanField(default=False)
    external_publication_date = models.DateField(null=True, blank=True, max_length=20)
    last_update = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return "%s - %s - %s" % (self.product_number, self.uilc, self.title)

    @models.permalink
    def get_absolute_url(self):
        return ('laws.views.view_wdetermination', [self.id])

    def get_ext_date(self):
        """Return external publication date"""
        return self.external_publication_date

    def get_name(self):
        return self._meta.verbose_name_plural

    class Meta:
        verbose_name_plural = "Written Determinations"    


class InternalRevenueManualToc(models.Model):
    """IRM table of contents,
    level = 0 - this is parts, like:
      Part 1
	    Organization, Finance and Management
      Part 2
	    Information Technology
    level = 1
       2.2  Partnership Control System
       and so on..."""
    toc = models.CharField(max_length=50)
    level = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=250)
    parent = models.ForeignKey('self', null=True)
    order_id = models.PositiveIntegerField(default=0)
    source_link = models.CharField(max_length=100, null=True, blank=True)
    
    def __unicode__(self):
        return "%s - %s" % (self.toc, self.name)

    class Meta:
        ordering = ("order_id",)
        
class InternalRevenueManual(models.Model):
    toc = models.ForeignKey(InternalRevenueManualToc)
    text = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return self.toc


class InternalRevenueBulletinToc(models.Model):
    """IRB table of contents,
    level = 0 - this is parts, like:
      Part 1
	    Organization, Finance and Management
      Part 2
	    Information Technology
    level = 1
       2.2  Partnership Control System
       and so on..."""
    IRB_DOC_TYPES = (
        (0, "Toc element"),
        (1, "Document"),
        (2, "Section"),
        )
    toc = models.CharField(max_length=50)
    level = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=250)
    parent = models.ForeignKey('self', null=True)
    order_id = models.PositiveIntegerField(default=0)
    element_type = models.PositiveIntegerField(choices=IRB_DOC_TYPES)
    source_link = models.CharField(max_length=100, null=True, blank=True)
    pdf_link = models.CharField(max_length=100, null=True, blank=True)
    current_through = models.DateField(null=True, blank=True)
    document = models.FileField(blank=True, null=True,
                                upload_to="uploads/documents/")
    section_id = models.CharField(max_length=20, null=True, blank=True)
    note = models.CharField(max_length=512, null=True, blank=True)
    
    def __unicode__(self):
        return "%s - %s" % (self.toc, self.name)

    class Meta:
        ordering = ("order_id",)
        
class InternalRevenueBulletin(models.Model):
    toc = models.ForeignKey(InternalRevenueBulletinToc)
    text = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.toc


class PdfHash(models.Model):
    """We store all hashes for objects with PDF documents,
    so we can find duplicates"""
    
    pdfhash = models.CharField(max_length=512)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    
    def __unicode__(self):
        return self.pdfhash[:20]

    class Meta:
        unique_together = (("object_id", "content_type"),)

class DuplicateDocument(models.Model):
    """Here we store duplicate documents
    we store them separately from PdfHash for performance"""
    
    duplicate_from = models.ForeignKey(PdfHash, related_name="duplicate_from")
    duplicate_to =  models.ForeignKey(PdfHash, related_name="duplicate_to")
    
    def __unicode__(self):
        return self.duplicate_from.pdfhash[:20]

    class Meta:
        unique_together = (("duplicate_from", "duplicate_to"),)
        
