from django.test import TestCase

from accounts.form import SingUpForm


class SignUpFormTest(TestCase):
    def test_form_has_fields(self):
        form = SingUpForm()
        expected = ['username', 'email', 'password1', 'password2', ]
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)
