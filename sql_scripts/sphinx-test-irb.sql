select a.id, 
(select id from django_content_type where model='internalrevenuebulletin' and app_label='laws') as content_type, 
	b.name as title, '' as description, '' as add_field, a.text, 
	EXTRACT( epoch FROM b.current_through) as ext_date, 
	NULL as last_update from laws_internalrevenuebulletintoc b, laws_internalrevenuebulletin a
 where a.toc_id=b.id; 