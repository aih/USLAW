alter table storeserver_link  add "decode_charset" varchar(50) NOT NULL default '';
ALTER TABLE plugins_plugin alter error type text;
ALTER TABLE plugins_update alter update_text type text;