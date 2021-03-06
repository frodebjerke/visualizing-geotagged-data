# Django settings for geotag project.
import os
import getpass

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
STATIC_PATH = os.path.join(PROJECT_PATH, "static")

UPLOAD_DIR = os.path.join(STATIC_PATH, "upload")
RES_DIR = os.path.join(PROJECT_PATH, "res")
MAP_DIR = os.path.join(RES_DIR, "map")
OUT_DIR = os.path.join(RES_DIR, "out")
TRACKS_DIR = os.path.join(RES_DIR, "tracks")
VIDEO_DIR = os.path.join(PROJECT_PATH, "videos")
EVALUATION_DIR = os.path.join(RES_DIR, "evaluation")
TEST_PATH = os.path.join(RES_DIR, "test")


LOG_PATH = os.path.join(PROJECT_PATH, "main.log")
MANAGERS = ADMINS


user = getpass.getuser()
# fredo can't use runserver with the database argument
# run it like export USE_SEMINAR_DB=True;python manage.py runserver 
if os.environ.has_key("USE_SEMINAR_DB"):
    user = "other"
    
DATABASE_PATH = os.path.join(PROJECT_PATH, "seminar.sqlite3")

import sys
# Creating a postgres database takes quite awhile. Sqlite3 is much faster.
if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(PROJECT_PATH, "test-db.sqlite3"),
        }
    }
# Inserting multiple records is slow with sqlite3.
elif user == "fredo" or user == "claus":
    DATABASES = {
                 'default': {
                             'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
                             'NAME': 'videotagging',  # Or path to database file if using sqlite3.
                             'USER': 'django',  # Not used with sqlite3.
                             'PASSWORD': 'django',  # Not used with sqlite3.
                             'HOST': 'localhost',  # Set to empty string for localhost. Not used with sqlite3.
                             'PORT': '5432',  # Set to empty string for default. Not used with sqlite3.
                             },
                 # for testing
                 'seminar': {
                             'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
                             'NAME': DATABASE_PATH,  # Or path to database file if using sqlite3.
                             }
                 }
# The postgres database adapter is hard to install on different systems.
# Sqlite3 comes with the standard python distribution
else:
    DATABASE_PATH = os.path.join(PROJECT_PATH, "seminar.sqlite3")
#    if not os.path.isfile(DATABASE_PATH):
#        raise RuntimeError, "Database %s does not exist. Did you run the setup.py script?" % DATABASE_PATH
    
    DATABASES = {
        'default': {
                    'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
                    'NAME': DATABASE_PATH,  # Or path to database file if using sqlite3.
                    }
    }

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'de-de'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = STATIC_PATH

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
                    os.path.join(PROJECT_PATH, 'static'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    "compressor.finders.CompressorFinder",
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '6t8&=c_sz!_+&n%s_ntpj=-ju++ts6plq4(hw-h)a$nb5=5c0)'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

COMPRESS_PRECOMPILERS = (
                         ("text/x-sass", "sass {infile} {outfile}"),
                         )

MIDDLEWARE_CLASSES = (
    'geo.middleware.NoSupportMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
)

# uses django compressor http://django_compressor.readthedocs.org/en/latest/settings/
# pip install django_compressor
INSTALLED_APPS = (
    "compressor",
    "geo",
    "info",
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
     'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)



# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters' : {
                    'verbose': {
                                'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
                                },
                    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'geo': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        '__main__': {
                     'handlers' : ['console'],
                     'level': 'DEBUG',
                     'propagate' : False
                     }
    }
}
