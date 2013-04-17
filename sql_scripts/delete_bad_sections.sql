delete from laws_subsection where section_id in (
       select max(id) from laws_section where section like '%-%' group by section, title_id, top_title_id, header having count(*)>1);

delete from laws_sectionadditional where section_id in (
       select max(id) from laws_section where section like '%-%' group by section, title_id, top_title_id, header having count(*)>1);

delete from laws_section where id in (
       select max(id) from laws_section where section like '%-%' group by section, title_id, top_title_id, header having count(*)>1);



delete from laws_subsection where section_id in (
       select id from laws_section
                where id in 
                    (select max(id) from laws_section group by section, title_id, top_title_id, replace(replace(header, '—', '  '), '-','') having count(*)>1) 
                  and header like '%-%'
);


delete from laws_sectionadditional where section_id in (
       select id from laws_section
                where id in 
                    (select max(id) from laws_section group by section, title_id, top_title_id, replace(replace(header, '—', '  '), '-','') having count(*)>1) 
                  and header like '%-%'
);


delete from laws_section
      where id in 
      (select max(id) 
      	      from laws_section 
              group by section, title_id, top_title_id, replace(replace(header, '—', '  '), '-','') 
	      having count(*)>1) 
      and header like '%-%';
