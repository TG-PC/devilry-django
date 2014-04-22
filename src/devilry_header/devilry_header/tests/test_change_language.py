from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.login import LoginTestCaseMixin



class TestChangeLanguage(TestCase, LoginTestCaseMixin):
    def setUp(self):
        self.url = reverse('devilry_change_language')

    def test_not_authenticated(self):
        response = self.client.post(self.url)
        self.assertEquals(response.status_code, 302)

    def test_post_valid(self):
        testuser = UserBuilder('testuser')
        testuser.update_profile(
            languagecode='nb'
        )
        with self.settings(LANGUAGES=[('en', 'English')]):
            response = self.post_as(testuser.user, self.url, {
                'languagecode': 'en',
                'redirect_url': '/successtest'
            })
            self.assertEquals(response.status_code, 302)
            self.assertEquals(response['Location'], 'http://testserver/successtest')
            testuser.reload_from_db()
            self.assertEquals(testuser.user.devilryuserprofile.languagecode, 'en')

    def test_post_invalid(self):
        testuser = UserBuilder('testuser')
        testuser.update_profile(
            languagecode='nb'
        )
        with self.settings(LANGUAGES=[('en', 'English')]):
            response = self.post_as(testuser.user, self.url, {
                'languagecode': 'tu',
                'redirect_url': '/successtest'
            })
            self.assertEquals(response.status_code, 400)
            testuser.reload_from_db()
            self.assertEquals(testuser.user.devilryuserprofile.languagecode, 'nb')