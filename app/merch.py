"""Server-priced merchandise checkout. Fulfillment is manual in Stripe Dashboard."""
import os
from urllib.parse import urlparse
import stripe
from flask import Blueprint, jsonify, render_template, request

stripe.default_http_client = stripe.RequestsClient(timeout=15)

merch = Blueprint('merch', __name__)
SIZES = ('S', 'M', 'L', 'XL', 'XXL')
UNIT_AMOUNT = 20000


def shop_settings():
    shipping = os.getenv('SHOP_SHIPPING_DKK', '')
    amount = int(shipping) if shipping.isascii() and shipping.isdigit() and int(shipping) <= 1000 else None
    base = os.getenv('SHOP_BASE_URL', '').rstrip('/')
    parsed = urlparse(base)
    valid_url = parsed.scheme == 'https' and bool(parsed.netloc) and not parsed.path and not parsed.query and not parsed.fragment and not parsed.username
    available = tuple(s for s in SIZES if s in os.getenv('SHOP_AVAILABLE_SIZES', '').split(','))
    return {'sizes': SIZES, 'available_sizes': available, 'shipping_dkk': amount,
            'shop_ready': bool(os.getenv('SHOP_ENABLED') == 'true' and os.getenv('STRIPE_SECRET_KEY') and valid_url and amount is not None and available),
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
    try:
        result = stripe.checkout.Session.create(
            api_key=os.environ['STRIPE_SECRET_KEY'], mode='payment',
            payment_method_types=['card'], locale='da',
            line_items=[{'price_data': {'currency': 'dkk', 'unit_amount': UNIT_AMOUNT,
                                      'product_data': {'name': f'Hydepark and the Legalizers — T-shirt ({size})'}},
                         'quantity': quantity} for size, quantity in quantities.items()],
            shipping_address_collection={'allowed_countries': ['DK']},
            shipping_options=[{'shipping_rate_data': {'type': 'fixed_amount',
                'fixed_amount': {'amount': settings['shipping_dkk'] * 100, 'currency': 'dkk'},
                'display_name': 'Forsendelse i Danmark'}}],
            billing_address_collection='required',
            metadata={'shop': 'hydepark-merch'},
            success_url=settings['base_url'] + '/shop/tak?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=settings['base_url'] + '/shop?cancelled=1',
        )
        return jsonify(url=result.url)
    except stripe.StripeError:
        return jsonify(error='Betalingen kunne ikke startes. Prøv igen senere.'), 502


@merch.get('/shop/tak')
def thanks():
    paid = False
    session_id = request.args.get('session_id', '')
    if session_id.startswith('cs_') and len(session_id) < 256 and os.getenv('STRIPE_SECRET_KEY'):
        try:
            result = stripe.checkout.Session.retrieve(session_id, api_key=os.environ['STRIPE_SECRET_KEY'])
            paid = result.payment_status == 'paid' and result.metadata.get('shop') == 'hydepark-merch'
        except stripe.StripeError:
            pass
    return render_template('shop_thanks.html', paid=paid)
