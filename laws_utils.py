# -*- coding: utf-8 -*-
# Extract sections references

try:
    import re2 as re
except:
    import re
from collections import namedtuple

def found_sections(line):
    i = line.find('section')
    if 'psection' in line:
        return False
    if i>-1:
        start_pos = i - 20
        end_pos = i + len('section') + 40
        if start_pos<0:
            start_pos = 0
        if end_pos > len(line):
            end_pos = len(line)
        return line[start_pos:end_pos]
    return False

def extract_section(line):
    """
    Extact section references from line

    some examples:
    conferred by sections 1738, 1739, 1743, and 1744 of title 12; subchapter II of chapter 471 of title 49; or sections 1884, 1891-1902, and former section 1641(b)(2), of title 50, appendix;
    
    sections 125 and 191 of this title;
    section 8339(a) through (e), (n), (q), (r), or (s).

    """
    Section = namedtuple('Section', 'title_name, section_name, subsection_name')
    section = Section

    title_re = re.compile(r'section (?P<section>[\-\w]+)(?P<subsection>[\w\d()]*)[,]* of title (?P<title>\w+)', re.IGNORECASE)
    title_re2 = re.compile(r'sections (?P<section>[\-\w]+)(?P<subsection>[\w\d()]*) and (?P<section2>[\-\w]+)(?P<subsection2>[\w\d()]*)[,]* of title (?P<title>\w+)', re.IGNORECASE)
    title_re3 = re.compile(r"""sections\s*
(?P<section>[\-\w]+)(?P<subsection>[\w\d()]*), \s*
(?P<section2>[\-\w]+)(?P<subsection2>[\w\d()]*), \s* and \s*
(?P<section3>[\-\w]+)(?P<subsection3>[\w\d()]*) \s*
of \s* title \s* (?P<title>\w+)""", re.IGNORECASE+re.VERBOSE)

    title_re4 = re.compile(r"""sections\s* 
(?P<section>[\-\w]+)(?P<subsection>[\w\d()]*),\s*  
(?P<section2>[\-\w]+)(?P<subsection2>[\w\d()]*),\s* 
(?P<section3>[\-\w]+)(?P<subsection3>[\w\d()]*),\s*  and \s* 
(?P<section4>[\-\w]+)(?P<subsection4>[\w\d()]*)\s* 
of\s*  title\s*  (?P<title>\w+)""", re.IGNORECASE+re.VERBOSE)

    title_re5 = re.compile(r"""sections\s* 
(?P<section>[\-\w]+)(?P<subsection>[\w\d()]*),\s*
(?P<section2>[\-\w]+)(?P<subsection2>[\w\d()]*),\s*
(?P<section3>[\-\w]+)(?P<subsection3>[\w\d()]*),\s*
(?P<section4>[\-\w]+)(?P<subsection4>[\w\d()]*)\s*and\s*
(?P<section5>[\-\w]+)(?P<subsection5>[\w\d()]*)[,]*\s*
of\s* title\s* (?P<title>\w+)""", re.IGNORECASE+re.VERBOSE)



    section_re1 = re.compile(r'section (?P<section>[\-\w]+)(?P<subsection>[\w\d()]*)[,]* and (?P<section2>[\-\w]+)(?P<subsection2>[\w\d()]*)(?!of)', re.IGNORECASE)
    section_re2 = re.compile(r'section (?P<section>[\-\w]+)(?P<subsection>[\w\d()]*)[;|$|,| |.\n](?!of)', re.IGNORECASE)
    #section_re3 = re.compile(r'section[s] ([\-\w]+)([\w\d()]+), (\w+)([\w\d()]+)[;|$|,| |.\n](?!of)', re.IGNORECASE)
    #section_re4 = re.compile(r'section ([\-\w]+)[$, .\n)](?!of)', re.IGNORECASE)

    #subsection_re1 = re.compile(r'subsection ([\w\d()]+) of section ([\-\w]+)', re.IGNORECASE)
    #subsection_re2 = re.compile(r'subsection[s] ([\w\d()]+) and ([\w\d()]+) of section ([\-\w]+)', re.IGNORECASE)
    #subsection_re3 = re.compile(r'subsection[s] ([\w\d()]+), ([\w\d()]+) and ([\w\d()]+) of section ([\-\w]+)', re.IGNORECASE)
    
    #section_line = found_sections(line)

    r = title_re.match(line) # First case
    if r:
        section.section_name = r.group('section')
        section.subsection_name = r.group('subsection')
        section.title_name = r.group('title')
        return [section, ]

    r = title_re2.match(line) 
    if r:
        sections = []
        section.section_name = r.group('section')
        section.subsection_name = r.group('subsection')
        section.title_name = "" 
        sections.append(section)

        section.section_name = r.group('section2')
        section.subsection_name = r.group('subsection2')
        section.title_name = "" 
        sections.append(section)

        return sections

    r = title_re3.match(line) 
    if r:
        sections = []
        section.section_name = r.group('section')
        section.subsection_name = r.group('subsection')
        section.title_name = "" 
        sections.append(section)

        section.section_name = r.group('section2')
        section.subsection_name = r.group('subsection2')
        section.title_name = "" 
        sections.append(section)

        section.section_name = r.group('section3')
        section.subsection_name = r.group('subsection3')
        section.title_name = "" 
        sections.append(section)

        return sections

    r = title_re4.match(line) 
    if r:
        sections = []
        section.section_name = r.group('section')
        section.subsection_name = r.group('subsection')
        section.title_name = "" 
        sections.append(section)

        section.section_name = r.group('section2')
        section.subsection_name = r.group('subsection2')
        section.title_name = "" 
        sections.append(section)

        section.section_name = r.group('section3')
        section.subsection_name = r.group('subsection3')
        section.title_name = "" 
        sections.append(section)

        section.section_name = r.group('section4')
        section.subsection_name = r.group('subsection4')
        section.title_name = "" 
        sections.append(section)

        return sections

    r = title_re5.match(line) 
    if r:
        sections = []
        section.section_name = r.group('section')
        section.subsection_name = r.group('subsection')
        section.title_name = "" 
        sections.append(section)

        section.section_name = r.group('section2')
        section.subsection_name = r.group('subsection2')
        section.title_name = "" 
        sections.append(section)

        section.section_name = r.group('section3')
        section.subsection_name = r.group('subsection3')
        section.title_name = "" 
        sections.append(section)

        section.section_name = r.group('section4')
        section.subsection_name = r.group('subsection4')
        section.title_name = "" 
        sections.append(section)

        section.section_name = r.group('section5')
        section.subsection_name = r.group('subsection5')
        section.title_name = "" 
        sections.append(section)

        return sections

    r = section_re1.match(line) 
    if r:
        sections = []
        if "(" not in r.group('subsection'):
            section.section_name = r.group('section')+r.group('subsection')
            section.subsection_name = ""
        else:
            section.section_name = r.group('section')
            section.subsection_name = r.group('subsection')
        section.title_name = "" 
        sections.append(section)

        if "(" not in r.group('subsection2'):
            section.section_name = r.group('section2')+r.group('subsection2')
            section.subsection_name = ""
        else:
            section.section_name = r.group('section2')
            section.subsection_name = r.group('subsection2')
        section.title_name = "" 
        sections.append(section)



        return sections

    r = section_re2.match(line) 
    if r:
        sections = []
        if "(" not in r.group('subsection'):
            section.section_name = r.group('section')+r.group('subsection')
        else:
            section.section_name = r.group('section')
            section.subsection_name = r.group('subsection')
        section.title_name = "" 
        sections.append(section)
        return sections

    """
    r = section_re1.findall(line)
    if r:
        return "1 section %s subsection %s, section %s subsection %s"%(r[0][0], r[0][1], r[0][2], r[0][3])

    r = section_re2.findall(line)
    if r:
        if "(" in r[0][1] and ")" in r[0][1]:
            return "2 section %s subsection %s, "%(r[0][0], r[0][1],)

    r = section_re3.findall(line)
    if r:
        return "3 %s"% r
        #return "3 section %s sub %s section %s, section %s subsection %s"%(r[0][0], r[0][1], r[0][2], r[0][3])

    r = section_re4.findall(line)
    if r:
        #print r
        return "4 section %s "%(r)

    r = subsection_re1.findall(line)
    if r:
        #print r
        return " subsection %s "%(r)
      """  
    return None
    
if __name__=="__main__":
    data = open('sections_ref.log')
    for l in data.readlines():
        print l.strip(), '=>', extract_section(l.strip())
    data.close()
