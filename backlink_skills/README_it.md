# Skill open source per backlink e invii a directory di prodotti

> Creato da [Flaq.ai](https://flaq.ai/) per agenti di programmazione AI come Codex e Claude Code.

Un flusso recuperabile e basato su prove per inviare prodotti, software, startup, app e siti web a directory di prodotti e altri canali pubblici di scoperta. Verifica l'idoneità, evita duplicati, rispetta le autorizzazioni, conserva le verifiche manuali, usa dati veritieri e registra risultati verificabili.

Una directory può generare citazioni, traffico referral o backlink, ma il progetto **non garantisce** il posizionamento del link, l'attributo follow, l'approvazione, l'indicizzazione, il traffico o miglioramenti di ranking.

**Lingue:** [English](README_en.md) · [简体中文](README.md) · [繁體中文](README_tw.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [ไทย](README_th.md) · [Tiếng Việt](README_vi.md) · [Bahasa Indonesia](README_id.md) · [Español](README_es.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Italiano](README_it.md) · [Português](README_pt.md) · [Русский](README_ru.md) · [العربية](README_ar.md) · [हिन्दी](README_hi.md) · [Türkçe](README_tr.md) · [Nederlands](README_nl.md) · [Polski](README_pl.md)

## Ambito

- Schede di prodotti, software, strumenti AI, startup, aziende, app e siti
- Percorsi `Request app`, raccomandazioni, rivendicazioni di schede e candidature vendor
- Creazione autorizzata di account gratuiti o profili pubblici
- Invii tramite blog, articoli, notizie, community, e-mail e moduli di contatto
- Controlli su idoneità, costi, link reciproci, account, duplicati e verifiche
- Stati supportati da prove e campagne riprendibili

## Principi di sicurezza

- Usa solo dati verificati su prodotto, azienda, fondatori, prezzi, contatti, proprietà e aspetti legali.
- Non aggirare CAPTCHA, Turnstile, 2FA, passkey o verifica e-mail.
- Non pagare, attivare rinnovi, aggiungere link reciproci, modificare sito/DNS, caricare file di verifica o rivendicare proprietà senza autorizzazione separata.
- Non considerare creazione account, bozza, clic o navigazione come pubblicazione.
- Se l'esito finale è ambiguo, indaga prima di riprovare per evitare duplicati.

## Flusso

1. Carica profilo, descrizioni, URL, risorse, regole di autorizzazione e registri approvati.
2. Normalizza e deduplica gli URL di destinazione.
3. Controlla disponibilità, idoneità, costi, reciprocità, account, termini e duplicati.
4. Raccogli CAPTCHA, e-mail, telefono e 2FA in un'unica coda manuale.
5. Dopo la verifica, inserisci solo fatti e risorse approvati.
6. Prima dell'azione finale ricontrolla costi, marchio, URL, categoria, upload, accordi, duplicati e autorizzazione.
7. Registra subito risposta esatta, orario, URL risultante e prove, quindi esegui l'audit.

## Utilizzo

Copia `submit-product-directories-v2-quality/` nella directory Skills dell'agente o fai riferimento diretto alla cartella.

```text
Usa $submit-product-directories-v2-quality per esaminare questi URL e preparare
una campagna. Controlla prima idoneità e verifiche. Non pubblicare, creare account,
accettare accordi o pagare senza autorizzazione. Salva un registro verificabile
e un'unica coda per le verifiche manuali.
```

```bash
python3 submit-product-directories-v2-quality/scripts/audit_submission_record.py path/to/record.md
python3 -m unittest discover -s submit-product-directories-v2-quality/tests
```

`submitted` richiede una ricevuta affidabile; `published` una pagina pubblica non di anteprima. Un clic o un reindirizzamento non dimostrano il successo.

## Flaq.ai e licenza

[Flaq.ai](https://flaq.ai/) offre accesso unificato a modelli di immagini, video, musica e linguaggio per agenti AI. Consulta [LICENSE](LICENSE).
