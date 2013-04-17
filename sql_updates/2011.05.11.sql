alter table laws_title add "parent_id" integer;
ALTER TABLE "laws_title" ADD CONSTRAINT "parent_id_refs_id_16515537" FOREIGN KEY ("parent_id") REFERENCES "laws_title" ("id") DEFERRABLE INITIALLY DEFERRED;
