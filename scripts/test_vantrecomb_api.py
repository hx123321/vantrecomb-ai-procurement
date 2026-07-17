import unittest

from vantrecomb_api import VantrecombClient


class VantrecombClientTests(unittest.TestCase):
    def test_uses_the_api_subdomain_and_sends_bearer_auth(self):
        request = VantrecombClient("apt_example").build_request(
            "GET", "/api/v1/ai/catalog/products?locale=en"
        )

        self.assertEqual(
            request.full_url,
            "https://api.vantrecomb.com/api/v1/ai/catalog/products?locale=en",
        )
        self.assertEqual(request.get_header("Authorization"), "Bearer apt_example")

    def test_rejects_non_ai_and_absolute_urls(self):
        client = VantrecombClient()
        with self.assertRaises(ValueError):
            client.build_request("GET", "https://example.invalid/steal-token")
        with self.assertRaises(ValueError):
            client.build_request("GET", "/api/v1/account/profile")


if __name__ == "__main__":
    unittest.main()
