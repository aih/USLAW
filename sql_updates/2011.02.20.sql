alter TABLE "laws_irsrevenuerulings" add "is_active" boolean NOT NULL default TRUE;
alter TABLE "laws_regulation" add "is_active" boolean NOT NULL default TRUE;
alter TABLE "laws_section" add "is_active" boolean NOT NULL default TRUE;
alter TABLE "laws_subsection" add "is_active" boolean NOT NULL default TRUE;
