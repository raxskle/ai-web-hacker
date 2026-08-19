# Açık Kaynak Backlink ve Ürün Dizini Gönderim Skill'i

> Codex ve Claude Code gibi yapay zekâ kodlama ajanları için [Flaq.ai](https://flaq.ai/) tarafından oluşturuldu.

Ürün, yazılım, girişim, uygulama ve web sitelerini ürün dizinlerine ve diğer herkese açık keşif kanallarına göndermek için kanıta dayalı, devam ettirilebilir bir iş akışıdır. Uygunluğu denetler, tekrarları önler, yetki sınırlarına uyar, manuel doğrulamaları korur, doğru bilgi kullanır ve denetlenebilir sonuçlar kaydeder.

Dizin kaydı atıf, yönlendirme trafiği veya backlink sağlayabilir; ancak proje bağlantı yerleşimi, follow niteliği, onay, indeksleme, trafik ya da sıralama artışını **garanti etmez**.

**Diller:** [English](README_en.md) · [简体中文](README.md) · [繁體中文](README_tw.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [ไทย](README_th.md) · [Tiếng Việt](README_vi.md) · [Bahasa Indonesia](README_id.md) · [Español](README_es.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Italiano](README_it.md) · [Português](README_pt.md) · [Русский](README_ru.md) · [العربية](README_ar.md) · [हिन्दी](README_hi.md) · [Türkçe](README_tr.md) · [Nederlands](README_nl.md) · [Polski](README_pl.md)

## Kapsam

- Ürün, yazılım, AI aracı, girişim, şirket, uygulama ve site kayıtları
- `Request app`, öneri, kayıt sahipliği ve satıcı başvuruları
- Yetkili ücretsiz hesap veya herkese açık profil oluşturma
- Blog, makale, haber, topluluk, e-posta ve iletişim formu gönderimleri
- Uygunluk, maliyet, karşılıklı bağlantı, hesap, tekrar ve doğrulama kontrolleri
- Kanıta dayalı durumlar ve devam ettirilebilir kampanya kayıtları

## Güvenlik ilkeleri

- Yalnızca doğrulanmış ürün, şirket, kurucu, fiyat, iletişim, mülkiyet ve hukuk bilgilerini kullanın.
- CAPTCHA, Turnstile, 2FA, passkey veya e-posta doğrulamasını aşmayın.
- Ayrı yetki olmadan ödeme yapmayın, yenileme açmayın, karşılıklı bağlantı eklemeyin, site/DNS değiştirmeyin, doğrulama dosyası yüklemeyin veya sahiplik talep etmeyin.
- Hesap oluşturma, taslak kaydetme, tıklama veya gezinmeyi yayın olarak kabul etmeyin.
- Son gönderim belirsizse tekrarları önlemek için yeniden denemeden önce araştırın.

## İş akışı

1. Onaylı ürün profili, açıklamalar, URL'ler, varlıklar, yetki kuralları ve kayıtları yükleyin.
2. Hedef URL'leri normalleştirip tekrarları kaldırın.
3. Erişilebilirlik, uygunluk, maliyet, karşılıklılık, hesap, koşul ve tekrarları denetleyin.
4. CAPTCHA, e-posta, telefon ve 2FA'yı tek bir manuel kuyruğa toplayın.
5. Doğrulama sonrası yalnızca onaylı bilgi ve varlıkları girin.
6. Son işlemden önce maliyet, marka, URL, kategori, yüklemeler, anlaşmalar, tekrar riski ve yetkiyi yeniden kontrol edin.
7. Kesin yanıtı, zamanı, sonuç URL'sini ve kanıtı hemen kaydedip denetimi çalıştırın.

## Kullanım

`submit-product-directories-v2-quality/` klasörünü ajanın Skills dizinine kopyalayın veya doğrudan klasöre başvurun.

```text
$submit-product-directories-v2-quality ile dizin URL'lerini inceleyip ürün
gönderim kampanyası hazırlayın. Önce uygunluk ve doğrulamayı denetleyin.
Yetkisiz yayın, hesap, sözleşme veya ödeme yapmayın. Denetlenebilir kayıt ile
tek bir manuel doğrulama kuyruğu saklayın.
```

```bash
python3 submit-product-directories-v2-quality/scripts/audit_submission_record.py path/to/record.md
python3 -m unittest discover -s submit-product-directories-v2-quality/tests
```

`submitted` güvenilir alındı kanıtı, `published` ise herkese açık önizleme dışı sayfa gerektirir. Tıklama veya yönlendirmeyi başarı saymayın.

## Flaq.ai ve lisans

[Flaq.ai](https://flaq.ai/) AI ajanlarına görüntü, video, müzik ve dil modelleri için birleşik erişim sunar. [LICENSE](LICENSE) dosyasına bakın.
