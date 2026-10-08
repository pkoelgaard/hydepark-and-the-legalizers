# Stripe-test og DAO-fragt på EC2

Denne opdatering bygger videre på den allerede deployede merch-opdatering. Den indeholder kun ændrede/nye filer. Kopiér indholdet af `fragt-update` ind i repository-roden, og flet mapperne. Slet ikke andre projektfiler. Den tidligere `docs/SHOP-OPSAETNING.md` er historisk; brug denne vejledning til fragt og testopsætning.

## 1. Deploy kodeændringerne fra din Mac

I repository-mappen efter kopiering:

```bash
git status
git diff --stat
git diff
git add app/merch.py app/configure_shop_test.py app/templates/shop.html app/templates/shop_thanks.html app/static/js/shop.js docs/SHOP-FRAGT-OG-STRIPE-TEST.md tests/test_merch_shipping.py
git commit -m "Add DAO home delivery, free shipping and Stripe test setup"
git push
```

Vent på, at GitHub Actions-deployment er gennemført. Hvis deployment fejler, så løs den fejl, før du fortsætter.

## 2. Åbn en interaktiv terminal på EC2

AWS Console → EC2 → region Stockholm (`eu-north-1`) → Instances → den eksisterende Hydepark-server → Connect → Session Manager → Connect.

Tidligere instance-id: `i-0fca199034189d8cf`. Brug den aktuelle instance, hvis serveren er blevet udskiftet. Session Manager kræver, at serveren er SSM-managed, og at din AWS-bruger har adgang til at starte sessioner. Alternativt kan du bruge jeres eksisterende SSH-adgang. Ingen ny SSH-port er nødvendig med Session Manager.

Kommandoerne fra dette trin og frem køres PÅ SERVEREN, ikke i din Mac-terminal.

Kontrollér, at scriptet er deployet, og at servicen indlæser konfigurationsfilen:

```bash
ls -l /opt/hydepark/app/configure_shop_test.py
sudo systemctl show hydepark -p EnvironmentFiles
```

Den sidste kommando skal vise `/etc/hydepark-shop.env`. Hvis den mangler, installér følgende service-override. Det er også kompatibelt med fremtidige deployments:

```bash
sudo mkdir -p /etc/systemd/system/hydepark.service.d
sudo tee /etc/systemd/system/hydepark.service.d/shop.conf >/dev/null <<'EOF'
[Service]
EnvironmentFile=-/etc/hydepark-shop.env
EOF
sudo systemctl daemon-reload
```

## 3. Installér testnøglen uden at vise den

```bash
sudo python3 /opt/hydepark/app/configure_shop_test.py
```

Når scriptet spørger efter Stripe-testnøglen, indsæt din `sk_test_...`-nøgle eller en korrekt tilladt `rk_test_...`-nøgle, og tryk Enter. Indtastningen vises ikke. Der er ingen grund til at dele nøglen i chat, committe den eller indsætte den i en AWS Run Command. Hvis en restricted key anvendes, skal den kunne oprette og hente Checkout Sessions og have nødvendige tilladelser til de relaterede ressourcer; verificér med testbetalingen.

Scriptet opretter/opdaterer `/etc/hydepark-shop.env` med root som ejer og rettigheder 600. Eksisterende indstillinger med andre navne bevares. De følgende shopindstillinger erstattes:

```ini
STRIPE_SECRET_KEY=<din testnøgle, ikke vist>
SHOP_BASE_URL=https://hydepark-and-the-legalizers.dk
SHOP_SHIPPING_DKK=39
SHOP_AVAILABLE_SIZES=S,M,L,XL,XXL
SHOP_TEST_ONLY=true
SHOP_ENABLED=true
```

Det betyder, at testbetaling er aktiveret. En live-nøgle bliver afvist, mens `SHOP_TEST_ONLY=true`. Butikken bliver mærket TESTSHOP. Der oprettes ingen Shipmondo-forsendelser. Scriptet ændrer ikke Nginx, Terraform eller certifikater.

Genstart og kontrollér:

```bash
sudo systemctl restart hydepark
sudo systemctl is-active hydepark
curl --fail --silent http://127.0.0.1:5000/shop | python3 -c 'import sys; print("TESTSHOP vises:", "TESTSHOP" in sys.stdin.read())'
```

Forvent `active` og `TESTSHOP vises: True`. Vis ikke konfigurationsfilen med `cat`, og send ikke dens indhold i chat.

## 4. Test i browseren

Åbn præcis: https://hydepark-and-the-legalizers.dk/shop

Checkout accepteres kun fra domænet i `SHOP_BASE_URL`. Brug derfor ikke .com eller www-versionen til disse tests. En senere domæneopdatering kan gøre alle adresser anvendelige.

| Kurv | Varer | DAO hjemmelevering | Total |
| --- | ---: | ---: | ---: |
| 1 T-shirt | 200 kr. | 39 kr. | 239 kr. |
| 2 T-shirts | 400 kr. | 39 kr. | 439 kr. |
| 3 T-shirts | 600 kr. | 0 kr. | 600 kr. |

Gratis fragt udløses ved vareværdi mindst 499 kr., før fragt. Med de nuværende produkter rammes grænsen ved tre T-shirts. Den samme regel beregnes på serveren; et ændret beløb fra browseren accepteres ikke. Fjern en T-shirt fra en kurv med tre og kontrollér, at fragt igen bliver 39 kr.

Gennemfør checkout med:
- Kort: `4242 4242 4242 4242`
- Udløb: en fremtidig dato
- CVC: et vilkårligt trecifret tal
- En dansk testleveringsadresse og et testtelefonnummer

Bekræft korrekt fragt i Stripe Checkout før betaling. Efter betaling viser hjemmesiden, at testbetalingen lykkedes, og at der ikke bliver sendt varer. Find derefter betalingen i SAMME Stripe-sandbox som den nøgle, der blev installeret. Kontrollér beløb, størrelse, antal, levering og kontaktoplysninger. Kontrollér også, at afbrudt betaling bevarer kurven.

Der er ikke gennemført en rigtig Stripe-testbetaling i leverancen, fordi din nøgle ikke er tilgængelig her. Kodens betalingstests bruger simulerede Stripe-responser.

## 5. Shipmondo i denne version

Levering er DAO hjemmelevering (`daoHOME`). Der sendes ingen API-kald til Shipmondo, og der købes ingen labels. Når shoppen senere modtager rigtige betalinger, kan I oprette forsendelser manuelt i Shipmondo ud fra betalte ordrer i Stripe. Emballage er A4 Poly Mailer; mål og vej den færdigpakkede forsendelse, også ved flere T-shirts.

Valgfri DAO pakkeshop til 35 kr. er ikke aktiveret. Den kræver en rigtig pakkeshopvælger og lagring af den valgte pakkeshops id. Det er ikke tilstrækkeligt at vise endnu en pris i Stripe Checkout.

## 6. Fejlfinding

- Scriptfil mangler: deployment er ikke færdigt, eller opdateringens `app`-mappe er ikke kopieret til repository-roden.
- TESTSHOP vises ikke: tjek EnvironmentFiles, servicegenstart, nøglens test-prefix og domænet. Prøv genindlæsning af browseren.
- Betaling giver 403: besøg den præcise .dk-adresse uden www.
- Betaling giver 503: shopindstillingerne eller testnøglen mangler/er ugyldige for testtilstand.
- Betaling giver 502: tjek nøglens konto/sandbox og Stripe Workbench-fejl. En nøgle kan have rigtigt prefix og stadig være forkert eller mangle tilladelser.
- Service starter ikke: `sudo journalctl -u hydepark -n 40 --no-pager`. Del kun fejltekst, uden nøgler eller personoplysninger.

Du kan lukke checkout ved at sætte `SHOP_ENABLED=false` i `/etc/hydepark-shop.env` og genstarte servicen. Bevar testnøglen skjult ved redigering.

## 7. Senere skift til Lars

Test først med Lars' egne sandboxnøgler. Før åbning skal Lars' Stripe-konto være klar til live-betalinger, og virksomheds-, bank-, kvitterings- og handelsoplysninger skal være udfyldt korrekt. Installér derefter Lars' live-nøgle i serverens konfigurationsfil, sæt `SHOP_TEST_ONLY=false`, og genstart servicen. Konfigurationsscriptet i denne pakke er kun til test og accepterer ikke live-nøgler. Den tidligere anbefaling om kun at skifte nøgle skal suppleres med denne nye indstilling.

Ordrer håndteres fortsat manuelt i Stripe Dashboard. Automatisk behandling kræver en særskilt webhook/integration. Der er ingen automatisk lagerreservation. Brug aldrig testordrer som grundlag for køb af rigtige labels.

## Kilder

- https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connect-with-systems-manager-session-manager.html
- https://docs.stripe.com/api/checkout/sessions/create
- https://docs.stripe.com/testing
