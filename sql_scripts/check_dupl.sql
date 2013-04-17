select section_id, count(section_id) from laws_subsection where section_id in (select id from laws_section where title_id=2) and subsection='' group by section_id having count(section_id)>1;
