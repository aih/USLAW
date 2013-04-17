alter TABLE "laws_irsrevenuerulings" add "is_outdated" boolean NOT NULL default FALSE;
alter TABLE "laws_regulation" add "is_outdated" boolean NOT NULL default FALSE;
alter TABLE "laws_section" add "is_outdated" boolean NOT NULL default FALSE;
alter TABLE "laws_subsection" add "is_outdated" boolean NOT NULL default FALSE;
