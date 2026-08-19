# 開源外鏈與產品目錄提交 Skill

> 由 [Flaq.ai](https://flaq.ai/) 建立，適用於 Codex、Claude Code 等 AI 程式開發 Agent。

這是一套可稽核、可恢復的產品目錄提交流程，用於把產品、軟體、新創、應用程式與網站提交到產品目錄及其他公開發現管道。它協助 Agent 核查資格、避免重複提交、遵守授權邊界、保留人工驗證步驟、只提交真實資訊，並留下可由其他執行者接手的證據記錄。

目錄收錄可能帶來品牌引用、推薦流量或外鏈，但本專案**不保證**外鏈上線、連結屬性、審核通過、索引、流量或排名提升。

**語言：** [English](README_en.md) · [简体中文](README.md) · [繁體中文](README_tw.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [ไทย](README_th.md) · [Tiếng Việt](README_vi.md) · [Bahasa Indonesia](README_id.md) · [Español](README_es.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Italiano](README_it.md) · [Português](README_pt.md) · [Русский](README_ru.md) · [العربية](README_ar.md) · [हिन्दी](README_hi.md) · [Türkçe](README_tr.md) · [Nederlands](README_nl.md) · [Polski](README_pl.md)

## 支援內容

- 產品、軟體、AI 工具、新創、公司、應用程式與網站目錄
- `Request app`、推薦、認領條目與供應商申請
- 經授權的免費帳號或公開資料建立
- 部落格、文章、新聞、社群、電子郵件與聯絡表單投稿
- 資源頁、合作夥伴目錄與類似公開發現管道
- 資格、費用、互惠連結、帳號、重複項目與驗證檢查
- 有證據的狀態追蹤與可恢復活動記錄

## 安全邊界

- 僅使用已核實的產品、公司、創辦人、價格、聯絡、所有權與法律資訊。
- 不繞過 CAPTCHA、Turnstile、2FA、Passkey、電子郵件驗證或其他保護。
- 未經另行授權，不付款、不啟用續費、不新增互惠連結、不修改網站或 DNS、不上傳驗證檔、不認領所有權。
- 不把建立帳號、儲存草稿、點擊按鈕或頁面跳轉視為已發布。
- 最終提交結果不明時先調查，不可直接重試。

## 流程

1. 讀取已核准的產品資料、描述版本、URL、素材、授權規則與既有記錄。
2. 正規化並去除重複目標 URL。
3. 檢查可用性、適配度、費用、互惠連結、帳號、條款、重複項目與認領條件。
4. 將 CAPTCHA、電子郵件、手機、2FA 等人工驗證整理成單一排序佇列。
5. 驗證後只以核准的事實與素材填寫表單。
6. 最終操作前再次核對費用、品牌、標準 URL、分類、上傳、協議、重複風險與授權。
7. 立即記錄準確回應、時間、結果 URL 與證據。
8. 稽核記錄並分別報告各狀態。

## 使用方法

將 `submit-product-directories-v2-quality/` 複製到 Agent 支援的 Skills 目錄，或直接引用此資料夾：

```text
使用 $submit-product-directories-v2-quality 檢查這批目錄 URL，
並為我們的產品準備提交活動。先做資格與驗證掃描；未獲授權時，
不要發布、建立帳號、接受協議或付款。保存可稽核記錄，並把人工
驗證集中到一個佇列。
```

Agent 應先讀取 `SKILL.md`，再按需載入 `references/`。若沒有活動記錄，請複製 `assets/submission-record-template.md`。

## 狀態、稽核與測試

`submitted` 需要可靠回執；`awaiting email verification` 表示等待信箱驗證；`awaiting approval` 表示網站明確進入審核；`published` 需要公開且非預覽的產品頁；`submission outcome unknown` 必須先調查再重試；`submission failed` 需要明確失敗證據。

不能只憑點擊、跳轉、表單清空、按鈕停用或沒有錯誤推斷成功。

```bash
python3 submit-product-directories-v2-quality/scripts/audit_submission_record.py path/to/record.md
python3 submit-product-directories-v2-quality/scripts/audit_submission_record.py path/to/record.md --json
python3 -m unittest discover -s submit-product-directories-v2-quality/tests
```

## 關於 Flaq.ai

[Flaq.ai](https://flaq.ai/) 為 AI Agent 與生產應用提供圖片、影片、音樂及語言模型的統一存取。本專案由 Flaq AI 團隊維護。

相關合集：[Awesome Codex Skills](https://github.com/flaqai/awesome_codex_skills) · [Awesome Claude Code Skills](https://github.com/flaqai/awesome_claude_code_skills)

## 授權條款

請參閱 [LICENSE](LICENSE)。
