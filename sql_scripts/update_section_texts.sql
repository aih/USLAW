-- SQL script for updating section_text field with texts from subsections
-- Texts are not sorted, but it is used only for SphinxSearch

CREATE AGGREGATE sum(text) (
  SFUNC=textcat,
  STYPE=text
);

update laws_section a 
   set section_text = (
             select sum(b.text||' ') 
               from laws_subsection b 
              where b.section_id = a.id);
