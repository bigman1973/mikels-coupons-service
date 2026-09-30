import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from app import app


class RetiredCouponEndpointsTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_reports_retired_service(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()['retired'])

    def test_legacy_coupon_endpoints_are_unavailable(self):
        for endpoint in ('/api/coupon/generate', '/api/coupon/validate', '/api/coupon/use'):
            response = self.client.post(endpoint, json={})
            self.assertEqual(response.status_code, 410)
            self.assertFalse(response.get_json()['success'])


if __name__ == '__main__':
    unittest.main()
