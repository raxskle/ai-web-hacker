# オープンソースのバックリンク＆製品ディレクトリ投稿 Skill

> Codex や Claude Code などの AI コーディングエージェント向けに [Flaq.ai](https://flaq.ai/) が作成しました。

製品、ソフトウェア、スタートアップ、アプリ、Web サイトを製品ディレクトリや公開ディスカバリーチャネルへ投稿するための、証拠に基づく再開可能なワークフローです。適格性の確認、重複防止、権限管理、手動認証、正確な入力、監査可能な記録を支援します。

掲載により引用、参照トラフィック、バックリンクを得られる場合がありますが、リンク掲載、follow 属性、承認、インデックス、流入、順位向上は**保証しません**。

**言語：** [English](README_en.md) · [简体中文](README.md) · [繁體中文](README_tw.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [ไทย](README_th.md) · [Tiếng Việt](README_vi.md) · [Bahasa Indonesia](README_id.md) · [Español](README_es.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Italiano](README_it.md) · [Português](README_pt.md) · [Русский](README_ru.md) · [العربية](README_ar.md) · [हिन्दी](README_hi.md) · [Türkçe](README_tr.md) · [Nederlands](README_nl.md) · [Polski](README_pl.md)

## 対応範囲

- 製品、ソフトウェア、AI ツール、企業、アプリ、Web サイトの掲載
- `Request app`、推薦、掲載権限の申請、ベンダー申請
- 許可された無料アカウントや公開プロフィールの作成
- ブログ、記事、ニュース、コミュニティ、メール、問い合わせフォームへの投稿
- 適格性、料金、相互リンク、アカウント、重複、認証要件の確認
- 証拠付きステータス管理と再開可能なキャンペーン記録

## 安全上の原則

- 確認済みの製品・会社・創業者・料金・連絡先・所有権・法的情報だけを使用します。
- CAPTCHA、Turnstile、2FA、パスキー、メール認証を回避しません。
- 個別の許可なく支払い、自動更新、相互リンク、Web/DNS 変更、検証ファイルのアップロード、所有権申請を行いません。
- アカウント作成、下書き保存、クリック、画面遷移だけで公開済みと判断しません。
- 最終送信の結果が不明な場合は、重複防止のため再送前に調査します。

## ワークフロー

1. 承認済みの製品情報、説明文、URL、素材、権限ルール、既存記録を読み込みます。
2. 対象 URL を正規化し、重複を除きます。
3. 利用可否、適合性、料金、相互リンク、アカウント、規約、重複、申請種別を確認します。
4. CAPTCHA、メール、電話、2FA などを一つの手動対応キューにまとめます。
5. 認証後、承認済みの事実と素材だけでフォームを入力します。
6. 最終操作前に料金、ブランド、URL、カテゴリ、アップロード、同意、重複、権限を再確認します。
7. 正確な応答、時刻、結果 URL、証拠を直ちに記録し、監査します。

## 使い方

`submit-product-directories-v2-quality/` をエージェントの Skills ディレクトリへコピーするか、フォルダーを直接指定してください。

```text
$submit-product-directories-v2-quality を使ってディレクトリ URL を確認し、
製品投稿キャンペーンを準備してください。まず適格性と認証を確認し、
許可なしに公開、アカウント作成、規約同意、支払いをしないでください。
監査可能な記録と手動認証キューを保存してください。
```

```bash
python3 submit-product-directories-v2-quality/scripts/audit_submission_record.py path/to/record.md
python3 -m unittest discover -s submit-product-directories-v2-quality/tests
```

`submitted` は信頼できる受領証拠、`published` は公開済みの非プレビューページを必要とします。クリックやリダイレクトだけで成功と判断してはいけません。

## Flaq.ai とライセンス

[Flaq.ai](https://flaq.ai/) は AI エージェント向けに画像、動画、音楽、言語モデルへの統一アクセスを提供します。ライセンスは [LICENSE](LICENSE) を参照してください。
