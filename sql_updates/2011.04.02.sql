alter table "help_help" add "one_time_notice" boolean NOT NULL default False;

alter table "posts_post" add "source" varchar(200);
alter table "posts_rssfeed" add "channel_label" varchar(200);

