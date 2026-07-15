from django.http import HttpResponse
from django.contrib.messages import get_messages

from users.models import User, PermisosModulo, can_view_users

from .base_test import BaseTests

class PermissionTests(BaseTests):

    def setUp(self):
        super().setUp()
        user_to_edit_perms = User.objects.create_user(
            username='toeditperms__',email='example@mail.com',password='12345',
            **{'first_name':'Bob','last_name':'Doe','provincia':'ASD','municipio':'ASD',
                          'empresa':self.logged_user.empresa,'cuenta':self.logged_user.cuenta})
        PermisosModulo.objects.bulk_create(
            PermisosModulo(user=user_to_edit_perms, modulo=modulo, nivel='0')
            for modulo, _ in PermisosModulo._meta.get_field('modulo').choices
        )
        self.user_to_edit_perms = user_to_edit_perms

    def test_view_user_perms_possitive(self):
        self.assertLogin()
        response = self.client.get(f'/backoffice/users/permissions/{self.user_to_edit_perms.UserID}',follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response,template_name='account/users/permissions/form.html')

    def test_view_user_perms_unauth_user(self):
        self.assertLogin()
        response = self.client.get(f'/backoffice/users/permissions/{self.other_user.UserID}')
        self.assertEqual(response.status_code,302)

    def test_alter_user_perms_possitive(self):
        self.assertLogin()
        response = self.client.post(f'/backoffice/users/permissions/edit/{self.user_to_edit_perms.UserID}',data={
            'p_USR':'1'},format='json',follow=True)
        self.assertRedirects(response, expected_url='/backoffice/users')
        self.assertEqual(response.status_code,200)
        #After Editing
        self.user_to_edit_perms.refresh_from_db()
        self.assertTrue(can_view_users(self.user_to_edit_perms))

    def test_alter_user_perms_level_invalid(self):
        self.assertLogin()
        response = self.client.post(f'/backoffice/users/permissions/edit/{self.user_to_edit_perms.UserID}',data={
            'p_USR':'100'},format='json',follow=True)
        #After Editing with Error
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response,template_name='account/users/permissions/form.html')
