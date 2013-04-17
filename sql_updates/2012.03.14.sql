alter table laws_namedstatute add "top_title_id" integer REFERENCES "laws_title" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "laws_namedstatute_top_title_id" ON "laws_namedstatute" ("top_title_id");

