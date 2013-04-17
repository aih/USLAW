alter table laws_section add    "subtitle_id" integer REFERENCES "laws_title" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "laws_section_subtitle_id" ON "laws_section" ("subtitle_id");
alter table laws_title add     "url" varchar(255);
