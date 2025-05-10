from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from chat.models import ChatRoom, Message, AgentProfile
from django.utils import timezone

class ChatViewTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        # Create test room
        self.room = ChatRoom.objects.create(
            name="Test Room",
            created_by=self.user,
            agent="default_agent"
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def test_chat_room_creation(self):
        response = self.client.post(reverse('chat:create_chat_room'), {
            'name': 'New Test Room',
            'agent': 'default_agent'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(ChatRoom.objects.filter(name='New Test Room').exists())

    def test_chat_room_list(self):
        response = self.client.get(reverse('chat:chat_room_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/chat_room_list.html')

    def test_chat_room_detail(self):
        response = self.client.get(
            reverse('chat:chat_room', kwargs={'room_id': self.room.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/chat_room.html')

    def test_message_creation(self):
        response = self.client.post(
            reverse('chat:send_message', kwargs={'room_id': self.room.id}),
            {'content': 'Test message'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Message.objects.filter(content='Test message').exists())

    def test_clear_conversation(self):
        # Create test message
        Message.objects.create(
            room=self.room,
            sender=self.user,
            content="Test message"
        )
        response = self.client.post(
            reverse('chat:clear_conversation', kwargs={'room_id': self.room.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Message.objects.filter(room=self.room).count(), 0)

    def test_unauthorized_access(self):
        # Logout and try to access
        self.client.logout()
        response = self.client.get(reverse('chat:chat_room_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def tearDown(self):
        # Clean up after tests
        self.user.delete()
        self.room.delete()