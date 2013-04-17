alter table laws_irsrevenuerulings add  "last_update" timestamp with time zone;
alter table posts_rssfeed alter column last_update drop not null;