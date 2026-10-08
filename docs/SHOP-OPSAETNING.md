# Shop / Merch – opsætning

Denne pakke opdaterer den eksisterende Flask-hjemmeside med T-shirts i S, M, L, XL og XXL til 200 kr., kurv og Stripe Checkout. Ingen rigtige betalinger er aktiveret fra start.

## Installér opdateringen

Udpak denne ZIP og kopier indholdet af `merch-update` ind i dit eksisterende repository. Flet mapperne og erstat kun filer med samme navn. Slet ikke eksisterende filer. Pakken indeholder kun webshopændringer samt en systemd-service med en ekstra EnvironmentFile-linje. Terraform, workflows, Nginx og HTTPS-scripts er ikke med i pakken.

Hvis du har ændret `app/web.py`, `app/requirements.txt` eller systemd-servicen siden den vedhæftede projektversion, så flet ændringerne frem for at overskrive dem.

```bash
git diff --stat
git diff
git add app/web.py app/merch.py app/requirements.txt app/templates/shop.html app/templates/shop_thanks.html app/static/css/shop.css app/static/js/shop.js app/static/js/shop-success.js infra/systemd/hydepark.service docs/SHOP-OPSAETNING.md
git commit -m "Add merchandise shop and configurable Stripe checkout"
git push
```

Det eksisterende deploy-flow installerer Stripe-afhængigheden. Betaling forbliver lukket, indtil serveren er konfigureret.

## Stripe og fragt

Opret og verificér jeres Stripe-konto. Begynd i testtilstand. Aktivér kvitteringer og betalingsnotifikationer i Stripe Dashboard.

Opret på EC2-serveren `/etc/hydepark-shop.env` via jeres eksisterende administrative adgang. Hold filen uden for Git, og gør den kun læsbar for root (`sudo chmod 600 /etc/hydepark-shop.env`). Indsæt følgende indstillinger, med jeres egne værdier:

```ini
STRIPE_SECRET_KEY=INDSAET_JERES_TESTNOEGLE
SHOP_BASE_URL=https://hydepark-and-the-legalizers.dk
SHOP_SHIPPING_DKK=INDSAET_FRAGTPRIS_I_HELE_KRONER
SHOP_AVAILABLE_SIZES=S,M,L,XL,XXL
SHOP_ENABLED=false
```

Fragt kan sættes til 0, hvis I vil tilbyde gratis fragt. Den er ikke sat i leverancen. Levering er foreløbig begrænset til Danmark. `SHOP_AVAILABLE_SIZES` er en manuel liste; fjern udsolgte størrelser. Der er ingen lagerreservation eller automatisk lagerstyring. Maksimum er 10 T-shirts pr. ordre.

Shoppen bruger én officiel adresse til checkout. Besøg den adresse, der står i `SHOP_BASE_URL`, også under test. Hvis en kunde forsøger at betale fra et andet domæne eller www-versionen, bliver forespørgslen afvist. Konfigurér redirect til den officielle shopadresse, hvis alle fire domæner skal kunne bruges til køb.

Når nødvendige oplysninger og test er klar, sæt `SHOP_ENABLED=true` og genstart:

```bash
sudo systemctl daemon-reload
sudo systemctl restart hydepark
sudo systemctl status hydepark --no-pager
```

Systemd indlæser filen ved hver genstart. Ingen hemmelig nøgle sendes til browseren. Prisen beregnes på serveren; en kundes egen pris i browseren bruges ikke.

## Inden åbning

Tilføj et rigtigt produktfoto og bekræft T-shirtens motiv, farve, pasform og materiale. Billedet i denne version er tydeligt mærket som et bandlogo og ikke et produktfoto.

Tilføj jeres sælgeroplysninger, handels- og returvilkår, leveringstid samt information om behandling af kundedata. Disse oplysninger er ikke opfundet i leverancen. Kontrollér også, at 200 kr. er den korrekte samlede salgspris i jeres konkrete momsopsætning; der bliver ikke lagt ekstra skat på i koden.

Test hele flowet med Stripe-testnøgle: flere størrelser, ændring/fjernelse i kurven, korrekt fragt, afbrudt betaling, vellykket betaling og betalt ordre i Dashboard med størrelse, antal og leveringsadresse. Stripe-testkort: 4242 4242 4242 4242, en fremtidig udløbsdato og en vilkårlig trecifret CVC. En faktisk testbetaling er ikke gennemført som del af leverancen, fordi der ikke er en Stripe-konto/nøgle til rådighed.

Efter gennemført test erstattes testnøglen med jeres live-nøgle, og servicen genstartes. Del ikke nøglen i chat eller Git.

## Sådan håndterer I ordrer

Brug Stripe Dashboard som ordrekilde. Se kun betalinger med gennemført status, kontrollér T-shirtstørrelse, antal, kundens e-mail og leveringsadresse, og send varerne. Registrér forsendelsen i jeres eget ordreskema eller med en intern note og trackingreference. Kontrollér Dashboard jævnligt, også hvis notifikationsmail udebliver.

Tak-siden kontrollerer betalingsstatus hos Stripe; den udløser ingen forsendelse. En kunde kan betale uden at vende tilbage til hjemmesiden. Derfor skal alle betalte ordrer behandles fra Stripe, uanset om tak-siden er besøgt. Der er ingen automatisk ordremail fra hjemmesiden, egen ordredatabase eller webhook i denne første version. Stripe-kvitteringer skal aktiveres separat. Automatisk ordrehåndtering kan tilføjes senere med verificerede webhooks.

Officiel dokumentation:
- https://docs.stripe.com/api/checkout/sessions/create
- https://docs.stripe.com/checkout/fulfillment
