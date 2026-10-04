#!/bin/bash
set -euo pipefail

DOMAIN="hydepark-and-the-legalizers.com"
WWW_DOMAIN="www.hydepark-and-the-legalizers.com"
DK_DOMAIN="hydepark-and-the-legalizers.dk"
DK_WWW_DOMAIN="www.hydepark-and-the-legalizers.dk"

for HOSTNAME in "$DOMAIN" "$WWW_DOMAIN" "$DK_DOMAIN" "$DK_WWW_DOMAIN"; do
  if ! getent hosts "$HOSTNAME" >/dev/null; then
    echo "DNS for $HOSTNAME does not resolve yet. Point the domain to this server first."
    exit 1
  fi
done

certbot --nginx \
  --non-interactive \
  --agree-tos \
  --redirect \
  --email peter@koelgaard.dk \
  -d "$DOMAIN" \
  -d "$WWW_DOMAIN" \
  -d "$DK_DOMAIN" \
  -d "$DK_WWW_DOMAIN"

systemctl reload nginx
