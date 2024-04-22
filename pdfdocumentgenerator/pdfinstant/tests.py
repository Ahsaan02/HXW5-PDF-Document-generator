from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
from django.contrib.auth import authenticate, login
from .forms import CSVUploadForm
from .views import parse_csv
from django.core.files.uploadedfile import SimpleUploadedFile
from django.middleware.csrf import get_token
from django.test import SimpleTestCase
from django.contrib.auth.hashers import check_password
from django.db import IntegrityError

#Unit Testing
class UserAccountTests(TestCase):
    def test_create_user_account(self):
        user = User.objects.create_user('testuser', 'test@example.com', 'mypassword')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(check_password('mypassword', user.password))

    def test_user_password_hashing(self):
        user = User.objects.create_user('testuser', 'test@example.com', 'mypassword')
        self.assertNotEqual(user.password, 'mypassword')  # Ensure password is hashed

    def test_duplicate_email_registration(self):
        User.objects.create_user('test@example.com', 'test@example.com', 'mypassword')
        with self.assertRaises(IntegrityError):  
            User.objects.create_user('test@example.com', 'test@example.com', 'mypassword2')

class CSVParserTest(SimpleTestCase):
    def test_parse_valid_csv(self):
        csv_content = "header1,header2\nvalue1,value2"
        expected_result = [{'header1': 'value1', 'header2': 'value2'}]
        result = parse_csv(csv_content)
        self.assertEqual(result, expected_result)

    def test_parse_csv_with_missing_values(self):
        csv_content = "header1,header2\nvalue1,"
        expected_result = [{'header1': 'value1', 'header2': ''}]
        result = parse_csv(csv_content)
        self.assertEqual(result, expected_result)

#Feature and Integration Testing

class TestLogin(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test@example.com', password='12345', email='test@example.com')

    def test_login_correct_credentials(self):
        response = self.client.post(reverse('signinaccount'), {'useremail': 'test@example.com', 'userpassword': '12345'})
        self.assertRedirects(response, reverse('homepage'))

    def test_login_incorrect_credentials(self):
        response = self.client.post(reverse('signinaccount'), {'useremail': 'test@example.com', 'userpassword': 'wrong'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Incorrect sign in details have been provided')

    def test_logout(self):
        self.client.login(username='test@example.com', password='12345')
        response = self.client.get(reverse('signout'))
        self.assertRedirects(response, reverse('signin'))

    def tearDown(self):
        self.client.session.clear()

class TestCSVUpload(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='securepassword')
        self.client.login(username='testuser', password='securepassword')

    def test_upload_correct_csv_file(self):
        csv_file = SimpleUploadedFile("test.csv", b"header1,header2\nvalue1,value2", content_type="text/csv")
        response = self.client.post(reverse('upload_csv'), {'file': csv_file})
        self.assertRedirects(response, reverse('template_choices'))

    def test_upload_incorrect_file_type(self):
        txt_file = SimpleUploadedFile("test.txt", b"This is not a CSV file.", content_type="text/plain")
        response = self.client.post(reverse('upload_csv'), {'file': txt_file})
        self.assertRedirects(response, reverse('upload_csv'))
        self.assertNotIn('csv_data', self.client.session)

    def tearDown(self):
        self.client.session.clear()


class TestPDFGeneration(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='securepassword')
        self.client.login(username='testuser', password='securepassword')

    def test_pdf_generation_with_valid_data(self):
        csv_data = "name,email\nAlice Smith,alice@example.com\nBob Brown,bob@example.com"
        session = self.client.session
        session['csv_data'] = csv_data
        session.save()
        response = self.client.post(reverse('process_csv'), {'template': 'template1', 'action': 'downloadZip'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('.zip' in response['Content-Disposition'])

    def test_session_cleanup_after_pdf_generation_and_zip_download(self):
        csv_data = "name,email\nAlicaean Smith,alicaean@example.com"
        session = self.client.session
        session['csv_data'] = csv_data
        session.save()
        self.client.post(reverse('process_csv'), {'template': 'template1', 'action': 'downloadZip'})
        self.assertNotIn('csv_data', self.client.session)

    def test_session_cleanup_after_pdf_generation_and_emailing(self):
        csv_data = "name,email\nAlicaean Smith,alicaean@example.com"
        session = self.client.session
        session['csv_data'] = csv_data
        session.save()
        self.client.post(reverse('process_csv'), {'template': 'template1', 'action': 'emailPdfs'})
        self.assertNotIn('csv_data', self.client.session)

    def tearDown(self):
        self.client.session.clear()

class CSRFProtectionTest(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='securepassword')
        self.client.login(username='testuser', password='securepassword')
        self.url = reverse('upload_csv') 

    def test_form_without_csrf(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 403)

    def test_form_with_csrf(self):
        response = self.client.get(self.url)
        csrf_token = get_token(response.wsgi_request)
        form_data = {'file': 'dummy_data'}
        response = self.client.post(self.url, form_data, HTTP_X_CSRFTOKEN=csrf_token)
        self.assertIn(response.status_code, [302, 200])
    
    def tearDown(self):
        self.client.session.clear()


class TestConcurrency(TestCase):
    def setUp(self):
        User.objects.create_user(username='user1', email='user1@example.com', password='password1')
        User.objects.create_user(username='user2', email='user2@example.com', password='password2')

    def test_concurrent_sessions(self):
        client1 = Client()
        client1.login(username='user1', password='password1')
        session1 = client1.session
        session1['csv_data'] = "name,email\nAlice Smith,alice@example.com"
        session1.save()

        client2 = Client()
        client2.login(username='user2', password='password2')
        session2 = client2.session
        session2['csv_data'] = "name,email\nBob Brown,bob@example.com"
        session2.save()

        response1 = client1.post(reverse('process_csv'), {'template': 'template1', 'action': 'downloadZip'})
        response2 = client2.post(reverse('process_csv'), {'template': 'template1', 'action': 'downloadZip'})

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertTrue('.zip' in response1['Content-Disposition'])
        self.assertTrue('.zip' in response2['Content-Disposition'])

    def tearDown(self):
        User.objects.all().delete()