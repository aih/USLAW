alter table laws_regulation add     "main_section_id" integer REFERENCES "laws_section" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "laws_regulation_main_section_id" ON "laws_regulation" ("main_section_id");
