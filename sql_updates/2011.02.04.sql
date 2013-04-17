-- Load irs rulings into new database structure

insert into laws_irsrevenuerulings (id, section, title, document, text, link, browsable, rate, publication_date) (select id, substring(title from 0 for 20), title, document, text, link, TRUE, 0, publication_date from laws_resource);