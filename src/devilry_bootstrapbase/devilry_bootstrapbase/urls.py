from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.i18n import javascript_catalog
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

from devilry_settings.i18n import get_javascript_catalog_packages
from .views import BootstrapExampleView


i18n_packages = get_javascript_catalog_packages(
    'devilry_extjsextras', 'devilry.apps.core')

urlpatterns = patterns('devilry_bootstrapbase',
        url('^example$', login_required(csrf_protect(ensure_csrf_cookie(BootstrapExampleView.as_view())))),
        url('^i18n.js$', javascript_catalog, kwargs={'packages': i18n_packages},
            name='devilry_bootstrapbase_i18n'))