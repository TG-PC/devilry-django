from django.utils.translation import ugettext_lazy as _
from django_cradmin import crmenu
from django_cradmin import crinstance

from devilry.apps.core.models import Period
from devilry.devilry_admin.views.period import overview
from devilry.devilry_admin.views.period import students
from devilry.devilry_admin.views.period import examiners
from devilry.devilry_admin.views.period import admins
from devilry.devilry_admin.views.period import createassignment
from devilry.devilry_admin.views.period import qualifiedforfinalexams


class Menu(crmenu.Menu):
    def build_menu(self):
        period = self.request.cradmin_role
        self.add_menuitem(
            label=period.short_name,
            active=self.request.cradmin_app.appname == 'overview',
            url=self.appindex_url('overview'))
        self.add_menuitem(
            label=_('Students'),
            active=self.request.cradmin_app.appname == 'students',
            url=self.appindex_url('students'))
        self.add_menuitem(
            label=_('Qualified for final exams'),
            active=self.request.cradmin_app.appname == 'qualifiedforfinalexams',
            url=self.appindex_url('qualifiedforfinalexams'))
        self.add_menuitem(
            label=_('Examiners'),
            active=self.request.cradmin_app.appname == 'examiners',
            url=self.appindex_url('examiners'))
        self.add_menuitem(
            label=_('Administrators'),
            active=self.request.cradmin_app.appname == 'admins',
            url=self.appindex_url('admins'))


class CrAdminInstance(crinstance.BaseCrAdminInstance):
    menuclass = Menu
    roleclass = Period
    apps = [
        ('overview', overview.App),
        ('students', students.App),
        ('examiners', examiners.App),
        ('admins', admins.App),
        ('createassignment', createassignment.App),
        ('qualifiedforfinalexams', qualifiedforfinalexams.App),
    ]
    id = 'devilry_admin_periodadmin'
    rolefrontpage_appname = 'overview'

    def get_rolequeryset(self):
        return Period.where_is_admin_or_superadmin(self.request.user)\
            .order_by('-start_time')

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is n Period.
        """
        period = role
        return period

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/devilry_admin/period')
