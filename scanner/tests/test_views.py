# scanner/tests/test_views.py

from django.test import TestCase, Client
from django.urls import reverse

class ScanViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('run_scan')  # adjust if your URL name differs

    def test_run_scan_no_url(self):
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('URL is required', response.json().get('error', ''))

    def test_run_scan_invalid_method(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_run_scan_valid_url(self):
        # This is a functional test hitting your real code,
        # but better to mock utils functions for unit tests.
        response = self.client.post(self.url, data={'url': 'https://example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.json())
        self.assertIsInstance(response.json()['results'], list)
        
    def test_scan_page_loads(self):
        response = self.client.get(reverse('scan_page'))