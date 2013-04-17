alter table "laws_regulation" add "current_through" date;

alter table "posts_rssfeed" add "frequency" integer NOT NULL default 30;
alter table "posts_rssfeed" add "publication_date" timestamp with time zone NOT NULL default NOW();
alter table "posts_rssfeed" add "site_url" varchar(250);
alter table "posts_rssfeed" add "last_update" timestamp with time zone NOT NULL default NOW(); 
