alter table users_profile alter headline type varchar(2500);
alter table users_profile alter location type varchar(2500);
alter table users_profile alter industry type varchar(2500);
alter table users_profile alter summary type varchar(2500);
alter table users_profile alter specialties type varchar(2500);
alter table users_profile alter interests type varchar(2500);
alter table users_profile alter honors type varchar(2500);

alter table users_education alter school_name type varchar(2512) ;
alter table users_education alter field_of_study type varchar(250);
alter table users_education alter start_date type varchar(50);
alter table users_education alter end_date type varchar(50);
alter table users_education alter degree type varchar(2512);
alter table users_education alter activities type varchar(2512);
alter table users_education alter notes type varchar(2512);

alter table users_position alter title type varchar(2512);
alter table users_position alter summary type text;
alter table users_position alter start_date type varchar(20);
alter table users_position alter end_date type varchar(20);
alter table users_position alter company type varchar(2512);
alter table users_position alter company_type type varchar(2512);
alter table users_position alter company_size type varchar(2512);
alter table users_position alter company_industry type varchar(2512);
alter table users_position alter company_ticker type varchar(2512);



