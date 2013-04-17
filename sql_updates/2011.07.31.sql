alter table laws_sectionadditional add "sa_type" integer NOT NULL;
alter table laws_subsection add "s_type" integer NOT NULL;

alter table entertainment_venue modify state  varchar(2) default null;
alter table entertainment_venue modify zip  varchar(30) default null;
alter table entertainment_venue modify `city_id` integer default null;


