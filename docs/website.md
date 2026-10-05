# Forside og undersider

Start lokalt: `python -m flask --app app.web run`.

Forside: `/`. Sider: `/tour`, `/bio`, `/music`, `/contact`, `/epk`, `/gallery`, `/shop`.

Ret `app/content.json` for koncertdata, kontaktadresser, eksternt nyhedsbrev, videoer og shop. URL-felter skal være betroede HTTPS-links. Koncerter har `date`, `venue`, `city`, `ticket_url`; videoer har `title`, `url`. Tomme lister viser tomme tilstande. Der er ikke oprettet en blog.

Formularen sender ikke data til en server: den klargør en tekst, som besøgende selv sender via Messenger. Tilslut en mailtjeneste før automatisk afsendelse; nyhedsbrev kræver et rigtigt tilmeldingslink. Ingen tilmeldinger gemmes.

Musik bruger de to eksisterende SoundCloud-demoer; ingen Spotify/Apple/Bandcamp-links er opfundet. Sangtekster, koncertarkiv, musikvideoer og teknisk rider kræver bandets materiale. Pressefotos og logo kan downloades fra EPK. Biografien er genbrugt fra den eksisterende EPK.
