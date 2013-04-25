USLAW
=====

Notes to restore from Amazon EC2/EB2

* Launch EC2 instance which includes an associated 22 GB EB2 storage
* Note that Apache server is no longer being used
* Servers are Nginx and fastcgi
* Edit the Nginx configuration in /etc/nginx/sites-available/default
*   change the domain designation
*   point to the correct filepath (e.g. starting with 'backup')
*   change the location directive to an alias directive from root

* Edit settings.py and local_settings.py
* Remove MEDIA_ROOT references except for the one in settings.py
* Make sure all paths are still correct, and domain references
* Make sure MEDIA_URL points to the whole url (www.domain.com, not just domain.com)
* 
* Restart Nginx
* go to the uslaw directory and run: $ sudo ./fcgi.sh
