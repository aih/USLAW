delete from laws_subsection where id in (select max(a.id) from laws_subsection a where subsection='' group by section_id having count(section_id)>1);
