Setup USLAW project
===================

Here is commands to setup uslaw server

First install software:

    sudo apt-get install nginx uwsgi python-virtualenv python-pip postgresql-9.1 postgresql-server-dev-9.1 mercurial git python-all-dev libxslt1-dev

Make directories:

    mkdir /mnt/www/beta.linkedlegislation.com
    cd  /mnt/www/beta.linkedlegislation.com

Clone project:

    git clone https://pi11@github.com/aih/USLAW src # don't forget to switch necessary branch 

We use virtualenv:

    virtualenv ../ve/
    source ../ve/bin/activate
    cd src

Install python libraries and dependencies:

    pip install -r requirements.txt


Now create role and database with commands:

    sudo su postgres
    psql

    create user "uslaw-beta" LOGIN UNENCRYPTED PASSWORD '__your_pass__' NOINHERIT VALID UNTIL 'infinity';
    CREATE DATABASE "uslaw-beta" ENCODING = 'UTF8' OWNER = "uslaw-beta" TEMPLATE = template0;
    \q

Copy and edit if necessary example congig files:
 
    cp example-configs/local_settings.py.template uslaw/local_settings.py
    cp example-configs/local_bot_settings.py.template uslaw/local_bot_settings.py


Init database and load fixtures:

    python manage.py syncdb 
    python manage.py loaddata fixtures/posts.json 
    python manage.py loaddata fixtures/plugins.json


Copy and edit example configs for nginx and uwsgi:

    cp example-configs/nginx-site.conf /etc/nginx/sites-available/beta.linkedlegislation.com.conf
    ln -s /etc/nginx/sites-available/beta.linkedlegislation.com.conf /etc/nginx/sites-enabled/beta.linkedlegislation.com.conf
    cp example-configs/uwsgi-site.conf /etc/uwsgi/apps-available/beta.linkedlegislation.com.conf
    ln -s /etc/uwsgi/apps-available/beta.linkedlegislation.com.conf /etc/uwsgi/apps-enabled/beta.linkedlegislation.com.conf

Start nginx and uwsgi:

    sudo /etc/init.d/nginx start
    sudo /etc/init.d/uwsgi start

Now perform some postgresql tuning:
Add these 2 lines at the end of /etc/sysctl.conf

    kernel.shmmax=2717986918
    kernel.shmall=1619430

Reboot server or execute commands:
    
    sysctl -n kernel.shmmax=2717986918
    sysctl -n kernel.shmall=1619430


Next edit /etc/postgresql/9.1/main/postgresql.conf and set shared_buffers = about 40% of memory (this is minimal changes required).

Next restart postgresql server:

    /etc/init.d/postgresql restart

Now we are done


