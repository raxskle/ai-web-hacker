# Open-source Skill do backlinków i zgłoszeń do katalogów produktów

> Utworzony przez [Flaq.ai](https://flaq.ai/) dla agentów programistycznych AI, takich jak Codex i Claude Code.

Oparty na dowodach, wznawialny proces zgłaszania produktów, oprogramowania, startupów, aplikacji i witryn do katalogów produktów oraz innych publicznych kanałów odkrywania. Skill sprawdza kwalifikację, zapobiega duplikatom, przestrzega uprawnień, zachowuje ręczne weryfikacje, używa prawdziwych danych i prowadzi audytowalny rejestr.

Wpis może przynieść wzmianki, ruch polecający lub backlinki, ale projekt **nie gwarantuje** umieszczenia linku, atrybutu follow, akceptacji, indeksacji, ruchu ani poprawy pozycji.

**Języki:** [English](README_en.md) · [简体中文](README.md) · [繁體中文](README_tw.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [ไทย](README_th.md) · [Tiếng Việt](README_vi.md) · [Bahasa Indonesia](README_id.md) · [Español](README_es.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Italiano](README_it.md) · [Português](README_pt.md) · [Русский](README_ru.md) · [العربية](README_ar.md) · [हिन्दी](README_hi.md) · [Türkçe](README_tr.md) · [Nederlands](README_nl.md) · [Polski](README_pl.md)

## Zakres

- Wpisy produktów, oprogramowania, narzędzi AI, startupów, firm, aplikacji i witryn
- Ścieżki `Request app`, rekomendacji, przejęcia wpisu i wniosku dostawcy
- Autoryzowane tworzenie darmowych kont lub profili publicznych
- Zgłoszenia przez blog, artykuł, wiadomości, społeczność, e-mail i formularz kontaktowy
- Kontrole kwalifikacji, kosztu, linku wzajemnego, konta, duplikatu i weryfikacji
- Statusy poparte dowodami i wznawialne rejestry kampanii

## Zasady bezpieczeństwa

- Używaj tylko zweryfikowanych informacji o produkcie, firmie, założycielach, cenach, kontakcie, własności i kwestiach prawnych.
- Nie obchodź CAPTCHA, Turnstile, 2FA, passkey ani weryfikacji e-mail.
- Bez osobnej zgody nie płać, nie włączaj odnowienia, nie dodawaj linku wzajemnego, nie zmieniaj witryny/DNS, nie przesyłaj pliku weryfikacyjnego i nie zgłaszaj własności.
- Nie uznawaj utworzenia konta, szkicu, kliknięcia ani nawigacji za publikację.
- Gdy wynik końcowy jest niejasny, zbadaj go przed ponowieniem, aby uniknąć duplikatu.

## Proces

1. Wczytaj zatwierdzony profil, opisy, URL-e, zasoby, reguły autoryzacji i istniejący rejestr.
2. Znormalizuj docelowe URL-e i usuń duplikaty.
3. Sprawdź dostępność, dopasowanie, koszt, wzajemność, konta, warunki i duplikaty.
4. Zbierz CAPTCHA, e-mail, telefon i 2FA w jednej kolejce ręcznej.
5. Po weryfikacji wprowadzaj tylko zatwierdzone fakty i zasoby.
6. Przed końcową akcją ponownie sprawdź koszt, markę, URL, kategorię, pliki, umowy, ryzyko duplikatu i uprawnienia.
7. Natychmiast zapisz dokładną odpowiedź, czas, wynikowy URL i dowody, a potem wykonaj audyt.

## Użycie

Skopiuj `submit-product-directories-v2-quality/` do katalogu Skills agenta albo wskaż folder bezpośrednio.

```text
Użyj $submit-product-directories-v2-quality, aby ocenić URL-e i przygotować
kampanię. Najpierw sprawdź kwalifikację i weryfikację. Bez zgody nie publikuj,
nie twórz kont, nie akceptuj umów i nie płać. Zapisz audytowalny rejestr oraz
jedną kolejkę ręcznych weryfikacji.
```

```bash
python3 submit-product-directories-v2-quality/scripts/audit_submission_record.py path/to/record.md
python3 -m unittest discover -s submit-product-directories-v2-quality/tests
```

`submitted` wymaga wiarygodnego potwierdzenia odbioru, a `published` publicznej strony niebędącej podglądem. Kliknięcie lub przekierowanie nie dowodzi sukcesu.

## Flaq.ai i licencja

[Flaq.ai](https://flaq.ai/) zapewnia agentom AI ujednolicony dostęp do modeli obrazu, wideo, muzyki i języka. Zobacz [LICENSE](LICENSE).
