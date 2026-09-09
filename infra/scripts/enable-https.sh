#!/bin/bash
set -euo pipefail

DOMAIN="hydepark-and-the-legalizers.com"
WWW_DOMAIN="www.hydepark-and-the-legalizers.com"

if ! getent hosts "$DOMAIN" >/dev/null; then
  echo "DNS for $DOMAIN does not resolve yet. Point the domain to this server first."
  exit 1
fi

certbot --nginx \
  --non-interactive \
  --agree-tos \
  --redirect \
  --email peter@koelgaard.dk \
  -d "$DOMAIN" \
  -d "$WWW_DOMAIN"

systemctl reload nginx
