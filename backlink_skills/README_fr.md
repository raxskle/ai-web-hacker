# Skill open source de soumission de backlinks et d'annuaires de produits

> Créé par [Flaq.ai](https://flaq.ai/) pour les agents de programmation IA comme Codex et Claude Code.

Un workflow traçable et reprenable pour soumettre des produits, logiciels, startups, applications et sites web à des annuaires de produits et autres canaux publics de découverte. Il vérifie l'éligibilité, évite les doublons, respecte les autorisations, conserve les validations manuelles, utilise des données exactes et produit un journal auditable.

Une fiche peut générer des citations, du trafic référent ou des backlinks, mais ce projet **ne garantit pas** le placement d'un lien, l'attribut follow, l'approbation, l'indexation, le trafic ou le classement.

**Langues :** [English](README_en.md) · [简体中文](README.md) · [繁體中文](README_tw.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [ไทย](README_th.md) · [Tiếng Việt](README_vi.md) · [Bahasa Indonesia](README_id.md) · [Español](README_es.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Italiano](README_it.md) · [Português](README_pt.md) · [Русский](README_ru.md) · [العربية](README_ar.md) · [हिन्दी](README_hi.md) · [Türkçe](README_tr.md) · [Nederlands](README_nl.md) · [Polski](README_pl.md)

## Périmètre

- Fiches de produits, logiciels, outils IA, startups, entreprises, applications et sites
- Parcours `Request app`, recommandation, revendication de fiche et candidature fournisseur
- Création autorisée de comptes gratuits ou profils publics
- Soumissions par blog, article, actualité, communauté, e-mail et formulaire de contact
- Contrôles d'éligibilité, coût, lien réciproque, compte, doublon et vérification
- Suivi des statuts avec preuves et campagnes reprenables

## Principes de sécurité

- Utiliser uniquement des informations vérifiées sur le produit, l'entreprise, les fondateurs, les prix, les contacts, la propriété et le juridique.
- Ne pas contourner CAPTCHA, Turnstile, 2FA, passkeys ou vérification d'e-mail.
- Ne pas payer, activer un renouvellement, ajouter un lien réciproque, modifier le site/DNS, téléverser un fichier de vérification ou revendiquer la propriété sans autorisation distincte.
- Ne pas confondre création de compte, brouillon, clic ou navigation avec publication.
- Si le résultat final est ambigu, enquêter avant toute nouvelle tentative pour éviter les doublons.

## Workflow

1. Charger le profil, les descriptions, URL, ressources, règles d'autorisation et journaux approuvés.
2. Normaliser et dédupliquer les URL cibles.
3. Vérifier disponibilité, adéquation, coût, réciprocité, comptes, conditions et doublons.
4. Regrouper CAPTCHA, e-mail, téléphone et 2FA dans une seule file manuelle.
5. Après validation, remplir uniquement avec les données et ressources approuvées.
6. Avant l'action finale, revérifier coût, marque, URL, catégorie, fichiers, accords, doublons et autorisation.
7. Consigner immédiatement réponse exacte, heure, URL obtenue et preuves, puis auditer.

## Utilisation

Copiez `submit-product-directories-v2-quality/` dans le dossier Skills de l'agent ou référencez directement le dossier.

```text
Utilise $submit-product-directories-v2-quality pour examiner ces URL et préparer
une campagne. Vérifie d'abord l'éligibilité et les validations. Ne publie pas,
ne crée pas de compte, n'accepte pas d'accord et ne paie pas sans autorisation.
Conserve un journal auditable et une file unique de validations manuelles.
```

```bash
python3 submit-product-directories-v2-quality/scripts/audit_submission_record.py path/to/record.md
python3 -m unittest discover -s submit-product-directories-v2-quality/tests
```

`submitted` exige une preuve de réception fiable ; `published`, une page publique hors aperçu. Un clic ou une redirection ne prouve jamais le succès.

## Flaq.ai et licence

[Flaq.ai](https://flaq.ai/) fournit un accès unifié aux modèles d'image, vidéo, musique et langage pour les agents IA. Voir [LICENSE](LICENSE).
