# Open-Source-Skill für Backlink- und Produktverzeichnis-Einreichungen

> Erstellt von [Flaq.ai](https://flaq.ai/) für KI-Coding-Agenten wie Codex und Claude Code.

Ein evidenzbasierter, fortsetzbarer Workflow zum Einreichen von Produkten, Software, Start-ups, Apps und Websites bei Produktverzeichnissen und anderen öffentlichen Discovery-Kanälen. Der Skill prüft Eignung, verhindert Duplikate, beachtet Autorisierungen, erhält manuelle Prüfungen, nutzt korrekte Daten und führt ein auditierbares Protokoll.

Verzeichniseinträge können Erwähnungen, Referral-Traffic oder Backlinks erzeugen. Dieses Projekt **garantiert jedoch nicht** die Platzierung, follow-Attribute, Freigabe, Indexierung, Traffic oder Rankingverbesserungen.

**Sprachen:** [English](README_en.md) · [简体中文](README.md) · [繁體中文](README_tw.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [ไทย](README_th.md) · [Tiếng Việt](README_vi.md) · [Bahasa Indonesia](README_id.md) · [Español](README_es.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Italiano](README_it.md) · [Português](README_pt.md) · [Русский](README_ru.md) · [العربية](README_ar.md) · [हिन्दी](README_hi.md) · [Türkçe](README_tr.md) · [Nederlands](README_nl.md) · [Polski](README_pl.md)

## Umfang

- Einträge für Produkte, Software, KI-Tools, Start-ups, Unternehmen, Apps und Websites
- `Request app`, Empfehlungen, Listing-Claims und Anbieterbewerbungen
- Autorisierte kostenlose Konten oder öffentliche Profile
- Blog-, Artikel-, News-, Community-, E-Mail- und Kontaktformular-Einreichungen
- Prüfung von Eignung, Kosten, Gegenlinks, Konten, Duplikaten und Verifizierung
- Evidenzbasierte Statusverfolgung und fortsetzbare Kampagnenprotokolle

## Sicherheitsgrundsätze

- Nur verifizierte Produkt-, Unternehmens-, Gründer-, Preis-, Kontakt-, Eigentums- und Rechtsdaten verwenden.
- CAPTCHA, Turnstile, 2FA, Passkeys und E-Mail-Verifizierung niemals umgehen.
- Ohne gesonderte Autorisierung nicht zahlen, verlängern, Gegenlinks setzen, Website/DNS ändern, Prüfdateien hochladen oder Eigentum beanspruchen.
- Kontoerstellung, Entwurf, Klick oder Navigation nicht als Veröffentlichung werten.
- Bei unklarem Endergebnis vor einem erneuten Versuch recherchieren, um Duplikate zu verhindern.

## Workflow

1. Freigegebenes Produktprofil, Texte, URLs, Assets, Autorisierungen und vorhandenes Protokoll laden.
2. Ziel-URLs normalisieren und deduplizieren.
3. Verfügbarkeit, Eignung, Kosten, Gegenlinks, Konten, Bedingungen und Duplikate prüfen.
4. CAPTCHA, E-Mail, Telefon und 2FA in einer manuellen Warteschlange sammeln.
5. Nach Verifizierung nur freigegebene Fakten und Assets eintragen.
6. Vor der finalen Aktion Kosten, Marke, URL, Kategorie, Uploads, Vereinbarungen, Duplikatrisiko und Freigabe erneut prüfen.
7. Exakte Antwort, Zeit, Ergebnis-URL und Belege sofort erfassen und das Protokoll auditieren.

## Verwendung

`submit-product-directories-v2-quality/` in das Skills-Verzeichnis des Agenten kopieren oder den Ordner direkt referenzieren.

```text
Nutze $submit-product-directories-v2-quality, um diese Verzeichnis-URLs zu prüfen
und eine Produktkampagne vorzubereiten. Prüfe zuerst Eignung und Verifizierung.
Ohne Autorisierung nicht veröffentlichen, registrieren, zustimmen oder zahlen.
Speichere ein auditierbares Protokoll und eine manuelle Prüfwarteschlange.
```

```bash
python3 submit-product-directories-v2-quality/scripts/audit_submission_record.py path/to/record.md
python3 -m unittest discover -s submit-product-directories-v2-quality/tests
```

`submitted` braucht einen verlässlichen Empfangsnachweis; `published` eine öffentliche Nicht-Vorschauseite. Ein Klick oder Redirect beweist keinen Erfolg.

## Flaq.ai und Lizenz

[Flaq.ai](https://flaq.ai/) bietet KI-Agenten einheitlichen Zugriff auf Bild-, Video-, Musik- und Sprachmodelle. Siehe [LICENSE](LICENSE).
