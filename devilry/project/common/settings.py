########################################################################
#
# Defaults for django settings
# - See: https://docs.djangoproject.com/en/dev/ref/settings/
#
########################################################################
import os
import devilry

from .projectspecific_settings import *  # noqa
from .django_cradmin_settings import *  # noqa


DEBUG = False
EXTJS4_DEBUG = DEBUG
TEMPLATE_DEBUG = DEBUG

TIME_ZONE = 'Europe/Oslo'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
FORMAT_MODULE_PATH = 'devilry.project.common.formats'
LOGIN_URL = '/authenticate/login'
STATIC_URL = '/static/'
STATIC_ROOT = 'static'
DATABASES = {}
EMAIL_SUBJECT_PREFIX = '[Devilry] '
ROOT_URLCONF = 'devilry.project.production.urls'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
AUTH_USER_MODEL = 'devilry_account.User'
LOGIN_REDIRECT_URL = '/'
CRISPY_TEMPLATE_PACK = 'bootstrap3'


INSTALLED_APPS = [
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.humanize',
    'errortemplates',
    'crispy_forms',
    'gunicorn',
    'extjs4',
    # 'haystack',
    'ievv_opensource.ievvtasks_common',
    'ievv_opensource.ievv_batchframework.apps.BatchOperationAppConfig',

    'devilry.devilry_bulkcreate_users',
    'devilry.devilry_cradmin',
    'django_cradmin',
    'django_cradmin.apps.cradmin_temporaryfileuploadstore',
    'devilry.django_decoupled_docs',

    'django_cradmin.apps.cradmin_authenticate',
    'devilry.devilry_resetpassword',
    'django_cradmin.apps.cradmin_resetpassword',
    'django_cradmin.apps.cradmin_generic_token_with_metadata',

    'devilry.apps.core.apps.CoreAppConfig',

    'devilry.devilry_account.apps.AccountAppConfig',
    'devilry.devilry_markup',
    'devilry.devilry_superadmin',
    'devilry.devilry_authenticate',
    'devilry.devilry_send_email_to_students',

    'devilry.devilry_help',
    'devilry.devilry_theme',
    'devilry.devilry_theme2',
    'devilry.devilry_theme3',
    'devilry.devilry_header',
    'devilry.devilry_frontpage',
    'devilry.devilry_student',
    'devilry.devilry_compressionutil',
    'devilry.devilry_group',
    'devilry.devilry_gradeform',
    'devilry.devilry_comment',
    'devilry.devilry_i18n',
    'devilry.devilry_settings',
    # 'devilry.devilry_search',
    'devilry.devilry_qualifiesforexam',
    # 'devilry.devilry_qualifiesforexam_approved',
    # 'devilry.devilry_qualifiesforexam_points',
    # 'devilry.devilry_qualifiesforexam_select',
    'devilry.devilry_examiner',
    'devilry.devilry_gradingsystem',
    'devilry.devilry_gradingsystemplugin_points.apps.GradingsystemPointsAppConfig',
    'devilry.devilry_gradingsystemplugin_approved.apps.GradingsystemApprovedAppConfig',
    'devilry.devilry_rest',
    'devilry.devilry_detektor',
    'devilry.devilry_admin',
    'devilry.project.common',

    # 'devilry.devilry_elasticsearch_cache.apps.ElasticsearchCacheAppConfig',
]

TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.request",
                               'django.contrib.messages.context_processors.messages',
                               'extjs4.context_processors.extjs4',
                               'devilry.project.common.templatecontext.template_variables',
                               'django_cradmin.context_processors.cradmin')


MIDDLEWARE_CLASSES = ['django.middleware.common.CommonMiddleware',
                      'django.contrib.sessions.middleware.SessionMiddleware',
                      'django.contrib.auth.middleware.AuthenticationMiddleware',
                      'devilry.devilry_i18n.middleware.LocaleMiddleware',
                      'django.contrib.messages.middleware.MessageMiddleware',
                      'devilry.utils.logexceptionsmiddleware.TracebackLoggingMiddleware']

##################################################################################
# Django Cradmin settings (Auth backend, forgotten password and sitename)
##################################################################################
AUTHENTICATION_BACKENDS = (
    'devilry.devilry_account.authbackend.default.EmailAuthBackend',
)


##################################################################################
#
# Haystack (search)
#
##################################################################################

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}
HAYSTACK_SIGNAL_PROCESSOR = 'devilry.devilry_search.haystack_signal_processor.DevilryCelerySignalProcessor'


########################################################################
#
# Celery
#
########################################################################
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_EAGER_TRANSACTION = True
CELERY_TIMEZONE = 'Europe/Oslo'
CELERY_ENABLE_UTC = True

# Celery settings
BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_IMPORTS = [
    'ievv_opensource.ievv_batchframework.celery_tasks',
]
CELERYD_TASK_LOG_FORMAT = '[%(asctime)s: %(levelname)s/%(processName)s] ' \
                          '[%(name)s] ' \
                          '[%(task_name)s(%(task_id)s)] ' \
                          '%(message)s'

# ievv_batchframework settings
IEVV_BATCHFRAMEWORK_CELERY_APP = 'devilry.project.common.celery_app'

# ievv_batchframework celery mode.
IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS = False


########################################################################
#
# i18n
#
########################################################################

#: Default language
LANGUAGE_CODE = 'en'

#: Available languages
gettext_noop = lambda s: s
LANGUAGES = [('en', gettext_noop('English')),
             ('nb', gettext_noop('Norwegian Bokmal'))]


LOCALE_PATHS = [
    os.path.join(
        os.path.abspath(os.path.dirname(devilry.__file__)),
        'locale')
]


###################################################
# Setup logging using the defaults - logs to stderr
###################################################
from devilry.project.log import create_logging_config
LOGGING = create_logging_config()
