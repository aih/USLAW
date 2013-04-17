select (select c.title 
          from laws_title c 
         where g.title_id=c.id) as title, g.section 
  from laws_section g 
 where g.id in (select id  
                  from laws_section a 
                 where not exists (select b.id 
                                     from laws_subsection b 
                                    where b.section_id=a.id)) 
                                      and not exists (select 1 
                                                        from laws_section e 
                                                       where e.title_id =g.title_id 
						         and e.id<>g.id 
						  	 and g.section like e.section||'%')
 order by 1,2;
