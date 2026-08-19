# Skill Open-Source untuk Pengiriman Backlink & Direktori Produk

> Dibuat oleh [Flaq.ai](https://flaq.ai/) untuk agen coding AI seperti Codex dan Claude Code.

Alur kerja berbasis bukti yang dapat dilanjutkan untuk mengirim produk, perangkat lunak, startup, aplikasi, dan situs web ke direktori produk serta kanal penemuan publik. Skill ini membantu memeriksa kelayakan, mencegah duplikasi, mematuhi batas otorisasi, mempertahankan verifikasi manual, memakai data yang benar, dan mencatat hasil yang dapat diaudit.

Daftar direktori dapat menghasilkan sitasi, trafik rujukan, atau backlink, tetapi proyek ini **tidak menjamin** penempatan tautan, atribut follow, persetujuan, pengindeksan, trafik, atau peningkatan peringkat.

**Bahasa:** [English](README_en.md) · [简体中文](README.md) · [繁體中文](README_tw.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [ไทย](README_th.md) · [Tiếng Việt](README_vi.md) · [Bahasa Indonesia](README_id.md) · [Español](README_es.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Italiano](README_it.md) · [Português](README_pt.md) · [Русский](README_ru.md) · [العربية](README_ar.md) · [हिन्दी](README_hi.md) · [Türkçe](README_tr.md) · [Nederlands](README_nl.md) · [Polski](README_pl.md)

## Cakupan

- Daftar produk, perangkat lunak, alat AI, startup, perusahaan, aplikasi, dan situs
- Jalur `Request app`, rekomendasi, klaim daftar, dan aplikasi vendor
- Pembuatan akun gratis atau profil publik jika diizinkan
- Pengiriman blog, artikel, berita, komunitas, email, dan formulir kontak
- Pemeriksaan kelayakan, biaya, tautan timbal balik, akun, duplikasi, dan verifikasi
- Pelacakan status berbasis bukti dan catatan kampanye yang dapat dilanjutkan

## Prinsip keselamatan

- Gunakan hanya fakta terverifikasi tentang produk, perusahaan, pendiri, harga, kontak, kepemilikan, dan aspek hukum.
- Jangan melewati CAPTCHA, Turnstile, 2FA, passkey, atau verifikasi email.
- Jangan membayar, mengaktifkan perpanjangan, menambah tautan timbal balik, mengubah situs/DNS, mengunggah berkas verifikasi, atau mengklaim kepemilikan tanpa izin terpisah.
- Jangan menganggap pembuatan akun, penyimpanan draf, klik, atau navigasi sebagai publikasi.
- Jika hasil pengiriman akhir tidak jelas, selidiki sebelum mencoba lagi untuk mencegah duplikasi.

## Alur kerja

1. Muat profil produk, deskripsi, URL, aset, aturan otorisasi, dan catatan yang disetujui.
2. Normalisasi dan hapus URL target duplikat.
3. Periksa ketersediaan, kecocokan, biaya, tautan timbal balik, akun, syarat, dan duplikasi.
4. Kumpulkan CAPTCHA, email, telepon, dan 2FA dalam satu antrean manual.
5. Setelah verifikasi, isi hanya fakta dan aset yang disetujui.
6. Sebelum tindakan akhir, periksa kembali biaya, merek, URL, kategori, unggahan, persetujuan, risiko duplikat, dan izin.
7. Catat respons, waktu, URL hasil, dan bukti segera, lalu audit catatan.

## Penggunaan

Salin `submit-product-directories-v2-quality/` ke direktori Skills agen atau rujuk folder tersebut secara langsung.

```text
Gunakan $submit-product-directories-v2-quality untuk meninjau URL direktori
dan menyiapkan kampanye pengiriman produk. Periksa kelayakan dan verifikasi
terlebih dahulu; jangan menerbitkan, membuat akun, menyetujui perjanjian,
atau membayar tanpa izin. Simpan catatan audit dan antrean verifikasi manual.
```

```bash
python3 submit-product-directories-v2-quality/scripts/audit_submission_record.py path/to/record.md
python3 -m unittest discover -s submit-product-directories-v2-quality/tests
```

`submitted` memerlukan bukti penerimaan yang andal; `published` memerlukan halaman publik non-pratinjau. Jangan menyimpulkan keberhasilan hanya dari klik atau pengalihan.

## Flaq.ai dan lisensi

[Flaq.ai](https://flaq.ai/) menyediakan akses terpadu ke model gambar, video, musik, dan bahasa untuk agen AI. Lihat [LICENSE](LICENSE).
