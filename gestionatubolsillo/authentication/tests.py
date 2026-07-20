from django.contrib.auth.models import AnonymousUser
from django.contrib.messages import get_messages
from home.tests import BaseTests

# Create your tests here.

class AuthTest(BaseTests):

    def test_login_possitive(self):
        self.assertLogin()

    def test_login_fails(self):
        response = self.client.post(path='/login',data={'username':'test_user','password':'incorrect'},format='json', follow=True)
        self.assertRedirects(response,expected_url='/login')
        self.assertEqual(response.status_code,200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages),1)
        self.assertEqual(messages[0].extra_tags,'error')
        self.assertEqual(str(messages[0]),"Credenciales inválidas. Por favor, inténtalo de nuevo.")

    def test_get_login_form_user_non_authenticated(self):
        response = self.client.get(path='/login',follow=True)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response,template_name='account/login.html')




    def test_logout(self):
        self.assertLogin()
        response = self.client.post(path='/logout',follow=True)
        self.assertRedirects(response,expected_url='/')
        self.assertEqual(response.status_code,200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertIsInstance(response.wsgi_request.user,AnonymousUser)

