"""Server-priced merchandise checkout. Fulfillment is manual in Stripe Dashboard."""
import os
from urllib.parse import urlparse
import stripe
from flask import Blueprint, jsonify, render_template, request

stripe.default_http_client = stripe.RequestsClient(timeout=15)

merch = Blueprint('merch', __name__)
SIZES = ('S', 'M', 'L', 'XL', 'XXL')
UNIT_AMOUNT = 20000
FREE_SHIPPING_AMOUNT = 49900


def shop_settings():
    shipping = os.getenv('SHOP_SHIPPING_DKK', '39')
    amount = int(shipping) if len(shipping) <= 4 and shipping.isascii() and shipping.isdigit() and int(shipping) <= 1000 else None
    base = os.getenv('SHOP_BASE_URL', '').rstrip('/')
    parsed = urlparse(base)
    valid_url = parsed.scheme == 'https' and bool(parsed.netloc) and not parsed.path and not parsed.query and not parsed.fragment and not parsed.username
    test_only = os.getenv('SHOP_TEST_ONLY', 'true') != 'false'
    key = os.getenv('STRIPE_SECRET_KEY', '')
    valid_key = key.startswith(('sk_test_', 'rk_test_')) if test_only else key.startswith(('sk_live_', 'rk_live_'))
    available = tuple(s for s in SIZES if s in os.getenv('SHOP_AVAILABLE_SIZES', '').split(','))
    return {'sizes': SIZES, 'available_sizes': available, 'shipping_dkk': amount, 'free_shipping_dkk': FREE_SHIPPING_AMOUNT // 100, 'test_only': test_only,
            'shop_ready': bool(os.getenv('SHOP_ENABLED') == 'true' and valid_key and valid_url and amount is not None and available),
            'base_url': base}


@merch.post('/shop/checkout')
def checkout():
    settings = shop_settings()
    if not settings['shop_ready']:
        return jsonify(error='Webshoppen er ikke åben for betaling endnu.'), 503
    # Browser requests must originate on the configured storefront. No cookie auth.
    if request.headers.get('Origin') != settings['base_url']:
        return jsonify(error='Ugyldig forespørgsel. Åbn shoppen på dens officielle adresse.'), 403
    data = request.get_json(silent=True)
    cart = data.get('items') if isinstance(data, dict) else None
    if not isinstance(cart, list) or not 1 <= len(cart) <= len(SIZES):
        return jsonify(error='Kurven er ugyldig.'), 400
    quantities = {}
    for item in cart:
        if not isinstance(item, dict):
            return jsonify(error='Kurven er ugyldig.'), 400
        size, quantity = item.get('size'), item.get('quantity')
        if not isinstance(size, str) or size not in settings['available_sizes'] or type(quantity) is not int or not 1 <= quantity <= 10 or size in quantities:
            return jsonify(error='Kontrollér størrelse og antal. Maks. 10 T-shirts pr. ordre.'), 400
        quantities[size] = quantity
    if sum(quantities.values()) > 10:
        return jsonify(error='Maks. 10 T-shirts pr. ordre.'), 400
    subtotal = sum(quantities.values()) * UNIT_AMOUNT
    shipping_amount = 0 if subtotal >= FREE_SHIPPING_AMOUNT else settings['shipping_dkk'] * 100
    try:
        result = stripe.checkout.Session.create(
            api_key=os.environ['STRIPE_SECRET_KEY'], mode='payment',
            payment_method_types=['card'], locale='da',
            line_items=[{'price_data': {'currency': 'dkk', 'unit_amount': UNIT_AMOUNT,
                                      'product_data': {'name': f'Hydepark and the Legalizers — T-shirt ({size})'}},
                         'quantity': quantity} for size, quantity in quantities.items()],
            shipping_address_collection={'allowed_countries': ['DK']},
            shipping_options=[{'shipping_rate_data': {'type': 'fixed_amount',
                'fixed_amount': {'amount': shipping_amount, 'currency': 'dkk'},
                'display_name': 'DAO hjemmelevering' + (' — gratis fragt' if shipping_amount == 0 else '')}}],
            billing_address_collection='required',
            phone_number_collection={'enabled': True},
            metadata={'shop': 'hydepark-merch', 'delivery_method': 'daoHOME', 'packaging': 'A4 poly mailer'},
            success_url=settings['base_url'] + '/shop/tak?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=settings['base_url'] + '/shop?cancelled=1',
        )
        return jsonify(url=result.url)
    except stripe.StripeError:
        return jsonify(error='Betalingen kunne ikke startes. Prøv igen senere.'), 502


@merch.get('/shop/tak')
def thanks():
    paid = False
    settings = shop_settings()
    session_id = request.args.get('session_id', '')
    if session_id.startswith('cs_') and len(session_id) < 256 and os.getenv('STRIPE_SECRET_KEY'):
        try:
            result = stripe.checkout.Session.retrieve(session_id, api_key=os.environ['STRIPE_SECRET_KEY'])
            paid = result.payment_status == 'paid' and (result.to_dict().get('metadata') or {}).get('shop') == 'hydepark-merch'
        except stripe.StripeError:
            pass
    return render_template('shop_thanks.html', paid=paid, test_only=settings['test_only'])
