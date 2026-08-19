# Open-source Skill voor backlinks en productdirectory-inzendingen

> Gemaakt door [Flaq.ai](https://flaq.ai/) voor AI-codeeragenten zoals Codex en Claude Code.

Een onderbouwde, hervatbare workflow voor het indienen van producten, software, startups, apps en websites bij productdirectory's en andere openbare discoverykanalen. De Skill controleert geschiktheid, voorkomt duplicaten, respecteert autorisaties, bewaart handmatige verificaties, gebruikt juiste gegevens en legt controleerbare resultaten vast.

Een vermelding kan citaties, verwijzingsverkeer of backlinks opleveren, maar dit project **garandeert geen** linkplaatsing, follow-attribuut, goedkeuring, indexering, verkeer of betere ranking.

**Talen:** [English](README_en.md) · [简体中文](README.md) · [繁體中文](README_tw.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [ไทย](README_th.md) · [Tiếng Việt](README_vi.md) · [Bahasa Indonesia](README_id.md) · [Español](README_es.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Italiano](README_it.md) · [Português](README_pt.md) · [Русский](README_ru.md) · [العربية](README_ar.md) · [हिन्दी](README_hi.md) · [Türkçe](README_tr.md) · [Nederlands](README_nl.md) · [Polski](README_pl.md)

## Reikwijdte

- Vermeldingen voor producten, software, AI-tools, startups, bedrijven, apps en sites
- `Request app`, aanbevelingen, listingclaims en leveranciersaanvragen
- Geautoriseerde gratis accounts of openbare profielen
- Inzendingen via blogs, artikelen, nieuws, community's, e-mail en contactformulieren
- Controle van geschiktheid, kosten, wederkerige links, accounts, duplicaten en verificatie
- Onderbouwde statussen en hervatbare campagnegegevens

## Veiligheidsprincipes

- Gebruik alleen geverifieerde product-, bedrijfs-, oprichters-, prijs-, contact-, eigendoms- en juridische gegevens.
- Omzeil geen CAPTCHA, Turnstile, 2FA, passkeys of e-mailverificatie.
- Betaal niet, activeer geen verlenging, plaats geen wederkerige link, wijzig geen website/DNS, upload geen verificatiebestand en claim geen eigendom zonder aparte toestemming.
- Beschouw accountaanmaak, conceptopslag, klikken of navigatie niet als publicatie.
- Onderzoek een onduidelijke einduitkomst vóór een nieuwe poging om duplicaten te voorkomen.

## Workflow

1. Laad goedgekeurd productprofiel, teksten, URL's, assets, autorisatieregels en bestaande gegevens.
2. Normaliseer doel-URL's en verwijder duplicaten.
3. Controleer beschikbaarheid, geschiktheid, kosten, wederkerigheid, accounts, voorwaarden en duplicaten.
4. Verzamel CAPTCHA, e-mail, telefoon en 2FA in één handmatige wachtrij.
5. Vul na verificatie alleen goedgekeurde feiten en assets in.
6. Controleer vóór de laatste actie opnieuw kosten, merk, URL, categorie, uploads, overeenkomsten, duplicaatrisico en toestemming.
7. Leg exacte reactie, tijd, resultaat-URL en bewijs direct vast en voer de audit uit.

## Gebruik

Kopieer `submit-product-directories-v2-quality/` naar de Skills-map van de agent of verwijs rechtstreeks naar de map.

```text
Gebruik $submit-product-directories-v2-quality om deze URL's te beoordelen en
een campagne voor te bereiden. Controleer eerst geschiktheid en verificatie.
Publiceer, registreer, accepteer of betaal niet zonder toestemming. Bewaar een
controleerbaar verslag en één wachtrij voor handmatige verificaties.
```

```bash
python3 submit-product-directories-v2-quality/scripts/audit_submission_record.py path/to/record.md
python3 -m unittest discover -s submit-product-directories-v2-quality/tests
```

`submitted` vereist betrouwbaar ontvangstbewijs; `published` een openbare pagina die geen preview is. Een klik of redirect bewijst geen succes.

## Flaq.ai en licentie

[Flaq.ai](https://flaq.ai/) biedt AI-agenten uniforme toegang tot beeld-, video-, muziek- en taalmodellen. Zie [LICENSE](LICENSE).
