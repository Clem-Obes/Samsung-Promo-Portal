"""
Comprehensive tests for the support app.
Covers: ContactMessage, ChatMessage, Comment models and views.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import ContactMessage, ChatMessage, Comment


class ContactMessageModelTest(TestCase):

    def test_create_message(self):
        msg = ContactMessage.objects.create(
            name='Test', email='test@test.com',
            subject='Help', message='I need help',
        )
        self.assertEqual(msg.status, 'unread')
        self.assertIn('Test', str(msg))


class ChatMessageModelTest(TestCase):

    def test_create_chat_message(self):
        user = User.objects.create_user('u', 'u@t.com', 'P!')
        msg = ChatMessage.objects.create(user=user, message='Hello')
        self.assertEqual(msg.sender, 'user')
        self.assertFalse(msg.is_read)


class CommentModelTest(TestCase):

    def test_create_comment(self):
        user = User.objects.create_user('u', 'u@t.com', 'P!')
        c = Comment.objects.create(user=user, content='Great site!')
        self.assertEqual(c.status, 'pending')


class ChatViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'Pass123!')

    def test_chat_requires_login(self):
        response = self.client.get(reverse('support:chat'))
        self.assertEqual(response.status_code, 302)

    def test_chat_loads(self):
        self.client.login(username='testuser', password='Pass123!')
        response = self.client.get(reverse('support:chat'))
        self.assertEqual(response.status_code, 200)

    def test_send_chat_message(self):
        self.client.login(username='testuser', password='Pass123!')
        response = self.client.post(reverse('support:chat'), {'message': 'Need help!'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ChatMessage.objects.filter(user=self.user, message='Need help!').exists())


class FaqViewTest(TestCase):

    def test_faq_page_loads(self):
        response = self.client.get(reverse('support:faq'))
        self.assertEqual(response.status_code, 200)
