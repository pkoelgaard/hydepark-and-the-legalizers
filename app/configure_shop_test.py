#!/usr/bin/env python3
"""Run interactively as root on EC2. Never prints or logs the Stripe key."""
import getpass
import os
from pathlib import Path
import tempfile


def main():
    if os.geteuid() != 0:
        raise SystemExit('Kør scriptet med sudo på EC2-serveren.')
    if not os.isatty(0):
        raise SystemExit('Brug en interaktiv Session Manager- eller SSH-terminal.')
    key = getpass.getpass('Indsæt Stripe-testnøglen (indtastning skjules): ').strip()
    if not key.startswith(('sk_test_', 'rk_test_')) or not key.isascii() or not all(c.isalnum() or c == '_' for c in key) or len(key) < 20:
        raise SystemExit('Der kræves en Stripe-testnøgle. Ingen fil blev ændret.')
    settings = {
        'STRIPE_SECRET_KEY': key,
        'SHOP_BASE_URL': 'https://hydepark-and-the-legalizers.dk',
        'SHOP_SHIPPING_DKK': '39',
        'SHOP_AVAILABLE_SIZES': 'S,M,L,XL,XXL',
        'SHOP_TEST_ONLY': 'true',
        'SHOP_ENABLED': 'true',
    }
    path = Path('/etc/hydepark-shop.env')
    previous = path.read_text() if path.exists() else ''
    remaining = [line for line in previous.splitlines() if line.partition('=')[0].strip() not in settings]
    content = '\n'.join(remaining + [f'{name}={value}' for name, value in settings.items()]) + '\n'
    fd, temporary = tempfile.mkstemp(prefix='.hydepark-shop-', dir='/etc')
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w') as output:
            output.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print('Testopsætning gemt. Nøglen er ikke vist. Kun testbetalinger er tilladt.')
    print('Genstart derefter: sudo systemctl restart hydepark')


if __name__ == '__main__':
    main()
