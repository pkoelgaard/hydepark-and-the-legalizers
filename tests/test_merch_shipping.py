"""Run after applying the update: python -m unittest discover -s tests."""
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
from web import app
from merch import FREE_SHIPPING_AMOUNT, shop_settings


class ShopShippingTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {
            'SHOP_ENABLED': 'true', 'SHOP_BASE_URL': 'https://hydepark-and-the-legalizers.dk',
            'STRIPE_SECRET_KEY': 'sk_test_example_only', 'SHOP_SHIPPING_DKK': '39',
            'SHOP_AVAILABLE_SIZES': 'S,M,L,XL,XXL', 'SHOP_TEST_ONLY': 'true',
        })
        self.env.start()
        self.addCleanup(self.env.stop)
        self.client = app.test_client()
        self.headers = {'Origin': 'https://hydepark-and-the-legalizers.dk'}

    def checkout(self, items):
        return self.client.post('/shop/checkout', json={'items': items}, headers=self.headers)

    def test_total_with_one_two_and_three_shirts(self):
        for quantity, expected_shipping in [(1, 3900), (2, 3900), (3, 0)]:
            with self.subTest(quantity=quantity), patch('merch.stripe.checkout.Session.create', return_value=SimpleNamespace(url='https://checkout.stripe.com/test')) as create:
                response = self.checkout([{'size': 'M', 'quantity': quantity, 'price': 1, 'shipping': 0}])
                self.assertEqual(response.status_code, 200)
                args = create.call_args.kwargs
                self.assertEqual(args['line_items'][0]['price_data']['unit_amount'], 20000)
                self.assertEqual(args['shipping_options'][0]['shipping_rate_data']['fixed_amount']['amount'], expected_shipping)
                self.assertEqual(args['metadata']['delivery_method'], 'daoHOME')
                self.assertEqual(args['shipping_address_collection']['allowed_countries'], ['DK'])
                self.assertTrue(args['phone_number_collection']['enabled'])

    def test_exact_free_shipping_boundary(self):
        # Existing catalog reaches 499 kr. at three shirts; simulate price to test exact boundary.
        self.assertEqual(FREE_SHIPPING_AMOUNT, 49900)
        for amount, expected in [(49899, 3900), (49900, 0)]:
            with patch('merch.UNIT_AMOUNT', amount), patch('merch.stripe.checkout.Session.create', return_value=SimpleNamespace(url='https://checkout.stripe.com/test')) as create:
                self.assertEqual(self.checkout([{'size': 'S', 'quantity': 1}]).status_code, 200)
                self.assertEqual(create.call_args.kwargs['shipping_options'][0]['shipping_rate_data']['fixed_amount']['amount'], expected)

    def test_different_sizes_combined(self):
        with patch('merch.stripe.checkout.Session.create', return_value=SimpleNamespace(url='https://checkout.stripe.com/test')) as create:
            self.assertEqual(self.checkout([{'size': 'S', 'quantity': 1}, {'size': 'XXL', 'quantity': 2}]).status_code, 200)
            self.assertEqual(create.call_args.kwargs['shipping_options'][0]['shipping_rate_data']['fixed_amount']['amount'], 0)

    def test_test_mode_refuses_live_key(self):
        with patch.dict(os.environ, {'STRIPE_SECRET_KEY': 'sk_live_example_only'}):
            self.assertFalse(shop_settings()['shop_ready'])
            self.assertEqual(self.checkout([{'size': 'S', 'quantity': 1}]).status_code, 503)

    def test_live_mode_refuses_test_key(self):
        with patch.dict(os.environ, {'SHOP_TEST_ONLY': 'false'}):
            self.assertFalse(shop_settings()['shop_ready'])

    def test_invalid_carts_and_unavailable_sizes(self):
        for items in [[], [{'size': 'S', 'quantity': True}], [{'size': 'S', 'quantity': 11}], [{'size': 'S', 'quantity': 6}, {'size': 'M', 'quantity': 5}], [{'size': 'S', 'quantity': 1}, {'size': 'S', 'quantity': 1}]]:
            self.assertEqual(self.checkout(items).status_code, 400)
        with patch.dict(os.environ, {'SHOP_AVAILABLE_SIZES': 'S'}):
            self.assertEqual(self.checkout([{'size': 'M', 'quantity': 1}]).status_code, 400)

    def test_wrong_origin(self):
        self.assertEqual(self.client.post('/shop/checkout', json={'items': [{'size': 'S', 'quantity': 1}]}).status_code, 403)

    def test_test_shop_notice_and_verified_success(self):
        self.assertIn(b'TESTSHOP', self.client.get('/shop').data)
        with patch('merch.stripe.checkout.Session.retrieve', return_value=SimpleNamespace(payment_status='paid', metadata={'shop': 'hydepark-merch'})):
            page = self.client.get('/shop/tak?session_id=cs_test_example').data
            self.assertIn('Testbetalingen lykkedes!'.encode(), page)
        with patch('merch.stripe.checkout.Session.retrieve', return_value=SimpleNamespace(payment_status='unpaid', metadata={'shop': 'hydepark-merch'})):
            self.assertNotIn(b'payment-confirmed', self.client.get('/shop/tak?session_id=cs_test_example').data)


if __name__ == '__main__':
    unittest.main()
