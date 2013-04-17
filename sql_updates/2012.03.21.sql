alter table laws_publication add "store_id" integer  REFERENCES "laws_textstore" ("id") DEFERRABLE INITIALLY DEFERRED;
-- Don't forget to run "python manage.py migrate_to_store" before droping column
alter table laws_publication drop column text;
