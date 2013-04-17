# -*- coding: utf-8 -*-
try:
    import re2 as re
except:
    import re
import traceback

from django import template
from django.utils.functional import allow_lazy
from django.template.defaultfilters import stringfilter

from laws.models import *

register = template.Library()

def reference_replace(matchobj):
    """
    Replace section/subsection/title reference with link to this section
    """
    new_value = ""
    if matchobj.group.has_key('subsection'):
        print ">>"
    #return 
    if len(matchobj.groups()) == 2:
        new_value = u"%s <div class='secbubble'><a class='sec' href='/laws/hoverbubble/?section=%s&title=26'>%s</a></div>" % (matchobj.group(1), matchobj.group(2), matchobj.group(2))

    if len(matchobj.groups()) == 4: # section, subsection, title
        print "%s, %s, %s, %s"%(matchobj.group(1), matchobj.group(2), matchobj.group(3),matchobj.group(4))
        """try:
            title = Title.objects.get(title=matchobj.group(4))
        except Title.DoesNotExist:
            title = False

        try:
            section = Section.objects.get(top_title=title, section=matchobj.group(1))
        except Section.DoesNotExist:
            section = False

        if matchobj.group(2):
            try:
                subsection = Subsection.objects.get(section=section, subsection=matchobj.group(2))
            except Subsection.DoesNotExist:
                subsection = False
        else:
            subsection = False
            
        if title and section and subsection:"""
        new_value = u"""
          <a class='sec' href='/laws/hoverbubble/?section_id=%s&context=hoverbubble'>%s</a>
          <a class='sec' href='/laws/hoverbubble/?section_id=%s&psection=%s&context=hoverbubble'>%s</a> %s %s
          """ % (section.id, matchobj.group(1), section.id, subsection.id, 
                 matchobj.group(2), matchobj.group(3), matchobj.group(4))

    #print new_value
    return new_value

@register.filter
def reference_links(value, top_title_id):
    return value
    """
    Replaces section references with corresponding link 
    examples:
       under subsection (b), (c), (m), or (o) of section 414 shall
       chapter 5 of title 5 
       subchapter III of chapter 33 of title 5.   
       of title 5
       Sec. 42.

       enacting sections 780a and 1901 to 1906 of this title, amending sections 706, 712 to 714, 720 to 722, 730, 732,
       741, 761 to 762a, 771, 772, 774, 775, 777, 777a, 777f, 780, 781,
       783, 791, 792, 794c, 795a, 795c, 795f, 795g, 795i, 796e, and 796i
       of this title and sections 6001, 6012, 6033, 6061, and 6081 of        Title 42,

       sections 202, 203 of this title

       sections 28b to 28e of this title
       sections 61 and 62 of this title
    second parameter in regexp lists is type of results:
       0 - section of current title
       1 - title in regexp

    """
    #return value
    if not value:
        return value
    # res_texts - regexp, and regexp types
    res_texts = [
                 [r"(?P<section>Section[\s\n\r]\d{1,6}[\-a-zA-Z]*)(?P<subsection>(\(.\))*)[\s\n\r]*of[\s\n\r]*this[\s\n\r]code", 0],
                 [r"(?P<section>Section[\s\n\r]\d{1,6}[\-a-zA-Z]*)(?P<subsection>(\(.\))*)[\s\n\r]*of[\s\n\r]*this[\s\n\r]title",0],
                 #[r"(?P<section>Sections\s\d{1,6}[a-zA-Z]*)\sand\s(?P<subsection>(\(.\))*)[,\s|\n]of[\s|\n]this[\s|\n]title",0],
                # [r"(Section\s[0-9.]+)\sor\s(?P<section>[\-\w]+)",0],
                # [r"(Sections\s[0-9.]+)\sand\s(?P<section>[\-\w]+)(?!(?:\sof))", 0],
                 #[r"(Section\s)(?P<section>[\-\w]+)(?!(?:\sof))", 0],
                 [r"(?P<section>Section[\s\n\r]\d{1,6}[\-a-zA-Z]*)(?P<subsection>(\(.\))*)(\s|[.;]|\))(?!(?:of|\[))",0],

                 [r"(?P<old_section>Sections[\s\n\r]\d{1,6}[\-a-zA-Z]*)(?P<old_subsection>(\(.\))*)\sand\s(?P<section>\d{1,6}[\-a-zA-Z]*)(?P<subsection>(\(.\))*)[\s\n\r]of[\s\n\r]this[\s\n\r]title", 0],


                 #[r"(?P<section>Sections[\s|\n]\d{1,6}[\-a-zA-Z]*)(?P<subsection>(\(.\))*)\sand\s(?P<old_section>\d{1,6}[\-a-zA-Z]*)(?P<old_subsection>(\(.\))*)[,\s|\n]of[\s|\n]this[\s|\n]title",0],
                 #[r"(?P<section_list>section[s]*\s[\d+\s,])[.]",2],

                 [r"(?P<section>Section[\s\n\r]\d{1,6}[\-a-zA-Z]*)(?P<subsection>(\(.\))*)[,\s\n\r$]+of[\s\n\r$]+(?P<title>title[\s]+\d+)",1],
                 #[r"(?P<section_list>(.*?)[.]|;|!|", 2],
                 [r"section\s(?P<section_list>[\d,orand\s\n\r]+)[\s\n\r]*of[\s\n\r]*this[\s\n\r]*title",2],
                 [r"section\s(?P<section_list>[\d,orand\s\n\r]+)[\s\n\r]*of[\s\n\r]*this[\s\n\r]*code",2],
                 ]
    result = value
    #print res_texts
    section_link_template = " <b>{{SECTION_TEXT}}</b> <a class='sec' href='/laws/hoverbubble/?section={{SECTION}}'>{{SECTION_NAME}}</a>"
    subsection_link_template = "<a class='sec' href='/laws/hoverbubble/?section={{SECTION}}&psection={{SUBSECTION}}&context=hoverbubble'>{{SUBSECTION_NAME}}</a>"
    title_link_template = "<b>Title</b> <a href='/laws/{{TITLE_NAME}}/'>{{TITLE_NAME}}</a>"
    replacements = []
    for r in res_texts:
        #print r
        #print r[0]
        regexp = re.compile(r[0], re.IGNORECASE+re.DOTALL)#re.MULTILINE+
        match_iter = regexp.finditer(result)#reference_replace, result)
        j = 0
        for m in match_iter:
            if r[1]<2:
                print "Found section %s, subsection %s" %(m.group('section'), m.group('subsection'))

            #print "RSIZE:", len(result)
            j += 1
            substr = result[m.start():m.end()]
            new_substr = False
#            if r[1]==3:
                
            if r[1]==2 or r[1]==3:
                if " of" in m.group("section_list"):
                    pass
                else:
                    section_list = m.group("section_list")
                    #subsections = re.compile(r"(\d{1,6}[a-zA-Z]*)\s|,|\(")
                    subsections = re.compile(r"(\d{1,6}[a-zA-Z]*)[\s,(]")
                    subs = subsections.findall(section_list)
                    #print "SUBS", subs
                    k = 0
                    for s in subs:
                        k += 1
                        print s
                        try:
                            section = Section.objects.get(top_title=top_title_id, section=s.strip())
                        except Section.DoesNotExist:
                            print "Section not found - %s - %s"%(s, top_title_id)
                            pass
                        else:
                            link_replace = section_link_template.replace('{{SECTION}}', str(section.id)).replace('{{SECTION_NAME}}', s).replace("{{SECTION_TEXT}}", "")
#m.group('section'))
                            if new_substr:
                                new_substr = new_substr.replace(s, link_replace)                    
                            else:
                                new_substr = substr.replace(s,link_replace)
                            
                    if new_substr:
                        #print "New substr", new_substr
                        replace_string = "{k"+str(j)+"}"
                        if len(replace_string)<len(substr):# we need to keep results size the same
                            replace_string = replace_string + substr
                            replace_string = replace_string[:len(substr)] #
                        #print result[m.start()-10:m.end()+25],">>", replace_string
                        result = result[:m.start()] + replace_string + result[m.end():]
                        #substr = "{"+j+"}"
                        replacements.append((replace_string, new_substr))

            #========================================================================================
            if r[1]==0 or r[1]==1: # current Title or title= thisprint m.group()
                if r[1]==1:
                    title_name = m.group('title').replace("title","").replace("Title","").strip()
                    #print "Title:", title_name
                    try:
                        title = Title.objects.get(title=title_name)
                    except Title.DoesNotExist:
                        continue
                    else:
                        title_link_replace = title_link_template.replace('{{TITLE}}', m.group('title')).replace('{{TITLE_NAME}}',title_name)
                        new_substr = substr.replace(m.group('title'), title_link_replace)
                        #print "TITLE founded in substring:", substr
                else:
                    title = top_title_id#Title.objects.get(pk=top_title_id)
                    
              
                #print r[0]
                try:
                    if "Section" in m.group('section'):
                        section_text = "Section"
                    else:
                        section_text = "section"
                    section_name = m.group('section').replace("Section", "").replace("section", '').strip()
                    section = Section.objects.get(top_title=title, section__iexact=section_name)
                except Section.DoesNotExist:
                    print "Section %s of Title %s does not exists" %(m.group('section'), title)
                    pass
                except:
                    print traceback.format_exc()
                else:
                    #print "Found section %s" %section
                    subsection_name = m.group('subsection').strip()
                    link_replace = section_link_template.replace('{{SECTION}}', str(section.id)).replace('{{SECTION_NAME}}', section_name).replace("{{SECTION_TEXT}}", section_text)
#m.group('section'))
                    if new_substr:
                        new_substr = new_substr.replace(m.group('section'), link_replace)
                    else:
                        new_substr = substr.replace(m.group('section'), link_replace)

                    if subsection_name!= "":
                        #print "Subsection", m.group('section'), m.group('subsection')
                        try:
                            subsection = Subsection.objects.get(section=section, 
                                                                subsection__iexact=subsection_name)
                        except (Subsection.DoesNotExist, Subsection.MultipleObjectsReturned):
                            print "Subsection not exists"#" - %s - %s"%(section, subsection_name)
                            #pass
                            
                        else:
                            #print "SUBSECTION: %s"%subsection.subsection
                            new_substr = new_substr.replace(
                                m.group('subsection'), 
                                subsection_link_template.replace('{{SECTION}}', str(section.id)).replace('{{SUBSECTION}}', subsection.subsection).replace('{{SUBSECTION_NAME}}',subsection.subsection)
                                )
                            #print "!!!", new_substr

                    #result = result.replace(substr, new_substr)
                    if new_substr:
                        #print "SUBSTR:", len(substr)
                        replace_string = "{"+str(j)+"}"
                        if len(replace_string)<len(substr):# we need to keep results size the same
                            replace_string = replace_string + substr
                            replace_string = replace_string[:len(substr)] #
                        #print result[m.start()-10:m.end()+25],">>", replace_string
                        result = result[:m.start()] + replace_string + result[m.end():]
                        #substr = "{"+j+"}"
                        replacements.append((replace_string, new_substr))
                        #print "New substr:", new_substr, "Will Replace this", replace_string
                        
                            #result = result.replace(

    
    for r in replacements:# we need this because if we  change result in list we fail
                          # with m.start()
        result = result.replace(r[0], r[1])
        #print r[0], r[1]
    return result

reference_links = stringfilter(reference_links)
reference_links.is_save=True
