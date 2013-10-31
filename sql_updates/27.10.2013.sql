alter table laws_subsection add "store_id" integer REFERENCES "laws_textstore" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "laws_subsection_store_id" ON "laws_subsection" ("store_id");

alter table laws_tmpsectionadditional add "store_id" integer REFERENCES "laws_textstore" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "laws_tmpsectionadditional_store_id" ON "laws_tmpsectionadditional" ("store_id");

alter table laws_sectionadditional add "store_id" integer REFERENCES "laws_textstore" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "laws_sectionadditional_store_id" ON "laws_sectionadditional" ("store_id");

alter table laws_regulation add "store_id" integer REFERENCES "laws_textstore" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "laws_regulation_store_id" ON "laws_regulation" ("store_id");

alter table laws_irsrevenuerulings add "store_id" integer REFERENCES "laws_textstore" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "laws_irsrevenuerulings_store_id" ON "laws_irsrevenuerulings" ("store_id");

alter table laws_irsprivateletter add "store_id" integer REFERENCES "laws_textstore" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "laws_irsprivateletter_store_id" ON "laws_irsprivateletter" ("store_id");

alter table laws_publaw add "store_id" integer REFERENCES "laws_textstore" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "laws_publaw_store_id" ON "laws_publaw" ("store_id");

alter table laws_formandinstruction add "store_id" integer REFERENCES "laws_textstore" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "laws_formandinstruction_store_id" ON "laws_formandinstruction" ("store_id");

alter table laws_decision add "store_id" integer REFERENCES "laws_textstore" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "laws_decision_store_id" ON "laws_decision" ("store_id");

alter table laws_internalrevenuebulletin add "store_id" integer REFERENCES "laws_textstore" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "laws_internalrevenuebulletin_store_id" ON "laws_internalrevenuebulletin" ("store_id");
