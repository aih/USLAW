alter table laws_section drop subtitle_id;
alter table laws_section add "top_title_id" integer REFERENCES "laws_title" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "laws_section_top_title_id" ON "laws_section" ("top_title_id");
