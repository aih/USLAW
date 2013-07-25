# Django settings for Tax26 project.
import os

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Serge', 'userge@list.ru'),
)

SETTINGS_ROOT = os.path.abspath(os.path.dirname(__file__))
MEDIA_ROOT = SETTINGS_ROOT+ "/site_media/"

MANAGERS = ADMINS

TIME_ZONE = 'America/Chicago'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'i6&q6kzw)6r_z(@yh6m!(dr4i$6_a#nla_hpnx77sq49c1#nm-'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (

#    'django.middleware.cache.UpdateCacheMiddleware',
#    'django.middleware.cache.FetchFromCacheMiddleware',
#    'utils.utils.SQLLogMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',

)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SETTINGS_ROOT, "templates"),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
 
    )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.flatpages',
    # 3rd party
    'django_extensions',
    'tinymce',
#   'tagging',
    # Project
    'laws',
#    'codeupdate',
    'users',
    'posts',
    'tags',
    'comment',
    'help',
    'document',
    'storeserver', 
    'log', 
    'plugins', 
    'api',
    'emailfeed',
)

LinkedInAPIKey = 'rbPThO1XDnQ45Kd9u1zB_3Hf3DdMlKh8PwcTcw6-oJpfEufHSs-ZUhOt9FjqT2LM'
LinkedInSecretKey = 'T8Ukw2YjDzjWsOUaYv0_M-wqD69dxN7WOvtD8K_6qZh094118VlDisIz0Fd9cRcf'
callbackurl = 'http://www.tax26.com/users/linkedin/'

TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,paste,searchreplace",
    'theme': "advanced",
    'theme_advanced_buttons1' : "bold,italic,underline,bullist,numlist,separator,outdent,indent,separator,undo,redo,separator,hr,removeformat,separator,justifyleft,justifycenter,justifyright,justifyfull",
    'theme_advanced_buttons2' : "",
    'theme_advanced_buttons3' : "",
    'width':'400',
    'height': '250',
}
TINYMCE_SPELLCHECKER = False

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'users.auth.LinkedInAuth', # if they fail the normal test
 )

APPEND_SLASH = True
from local_settings import *

