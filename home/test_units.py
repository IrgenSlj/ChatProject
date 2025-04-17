from django.test import TestCase
from django.urls import reverse

class HomeViewTest(TestCase):
    def test_home_view_returns_200(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_home_view_uses_correct_template(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'home/home.html')