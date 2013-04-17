create table reference_sections as select * from laws_section_reference_section;
insert into reference_sections (from_section_id, to_section_id) select a.section_id, b.section_id from laws_section_reference_subsection a, laws_subsection b where a.subsection_id =b.id;

select co, a.header from laws_section a, (
       select count(*) as co, a.id 
       	      from laws_section a, reference_sections b 
              where a.id=b.to_section_id 
              group by a.id 
   	      order by count(*) desc) b 
       where a.id=b.id;




select id from laws_title where title='26' and parent_id is null;

select e.id, e.section, e.header, f.co from
                   (select a.to_section_id as sid, count(a.*)/ 3 as co 
                         from (select b.id as from_section_id, 
                                      c.section_id as to_section_id
                                 from laws_section_reference_subsection c, 
                                      laws_section b, laws_subsection d 
                                where c.section_id=b.id 
                                  and d.id=c.subsection_id
                            union all select from_section_id, to_section_id
                                        from laws_section_reference_section) a
                        group by a.to_section_id 
                        order by count(a.*) desc 
                        limit 1500) f, laws_section e
                      where f.sid = e.id 
		       and e.top_title_id = 16484
                   order by f.co desc;