-- list of duplicates:

select name, count(*) from laws_title group by name, parent_id having count(*)>1;

-- delete duplicates


create or replace function delete_duplicate_sectiond(t_id integer) returns void as $$
BEGIN
	DELETE FROM laws_sectionadditional 
	WHERE  section_id IN (SELECT id 
			      FROM   laws_section 
			      WHERE  title_id = t_id); 

        DELETE FROM laws_subsection 
	WHERE  section_id IN (SELECT id 
			      FROM   laws_section 
			      WHERE  title_id = t_id); 


	DELETE FROM laws_section WHERE  title_id = t_id; 
        RAISE NOTICE 'Title ID is %', t_id;

END
$$ LANGUAGE plpgsql;


create or replace function delete_duplicate_titles(l integer) returns void as $$
DECLARE
r RECORD;
row_data RECORD;
BEGIN
    FOR  i IN 1..30 LOOP
    FOR r IN SELECT MAX(id) as id, name FROM laws_title GROUP BY NAME, parent_id HAVING COUNT(*) > 1 limit l LOOP
        RAISE NOTICE 'ID is %', r.id;
        RAISE NOTICE 'Name is %', r.name;
	PERFORM delete_duplicate_sectiond(r.id);
          FOR row_data in select * from laws_title where parent_id = r.id LOOP
              RAISE NOTICE 'Parent is %', row_data.parent_id;
              RAISE NOTICE 'Title is %', row_data.title;
	      RAISE NOTICE 'Name is %', row_data.name;
	      PERFORM delete_duplicate_sectiond(row_data.id);
          END LOOP;
	DELETE FROM laws_title 	WHERE  parent_id = r.id; 
	DELETE FROM laws_title 	WHERE  id = r.id; 
    END LOOP;
    END LOOP;
END;
$$ language  'plpgsql';