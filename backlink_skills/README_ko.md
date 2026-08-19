# 오픈 소스 백링크 및 제품 디렉터리 제출 Skill

> Codex, Claude Code 같은 AI 코딩 에이전트를 위해 [Flaq.ai](https://flaq.ai/)가 만들었습니다.

제품, 소프트웨어, 스타트업, 앱, 웹사이트를 제품 디렉터리와 공개 검색 채널에 제출하기 위한 증거 기반의 재개 가능한 워크플로입니다. 적격성 조사, 중복 방지, 권한 경계, 수동 인증, 사실 기반 입력, 감사 가능한 기록을 지원합니다.

디렉터리 등록은 인용, 추천 트래픽 또는 백링크를 만들 수 있지만 링크 게재, follow 속성, 승인, 색인, 트래픽 또는 순위 향상을 **보장하지 않습니다**.

**언어:** [English](README_en.md) · [简体中文](README.md) · [繁體中文](README_tw.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [ไทย](README_th.md) · [Tiếng Việt](README_vi.md) · [Bahasa Indonesia](README_id.md) · [Español](README_es.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Italiano](README_it.md) · [Português](README_pt.md) · [Русский](README_ru.md) · [العربية](README_ar.md) · [हिन्दी](README_hi.md) · [Türkçe](README_tr.md) · [Nederlands](README_nl.md) · [Polski](README_pl.md)

## 지원 범위

- 제품, 소프트웨어, AI 도구, 스타트업, 회사, 앱, 웹사이트 등록
- `Request app`, 추천 요청, 목록 소유권 주장, 공급업체 신청
- 승인된 무료 계정 또는 공개 프로필 생성
- 블로그, 기사, 뉴스, 커뮤니티, 이메일, 문의 양식 제출
- 적격성, 비용, 상호 링크, 계정, 중복, 인증 요구사항 점검
- 증거 기반 상태 추적과 재개 가능한 캠페인 기록

## 안전 원칙

- 검증된 제품, 회사, 창업자, 가격, 연락처, 소유권, 법률 정보만 사용합니다.
- CAPTCHA, Turnstile, 2FA, 패스키, 이메일 인증을 우회하지 않습니다.
- 별도 승인 없이 결제, 자동 갱신, 상호 링크, 웹사이트/DNS 변경, 인증 파일 업로드, 소유권 주장을 하지 않습니다.
- 계정 생성, 초안 저장, 클릭 또는 페이지 이동을 게시 완료로 간주하지 않습니다.
- 최종 제출 결과가 불명확하면 중복 방지를 위해 재시도 전에 조사합니다.

## 워크플로

1. 승인된 제품 프로필, 설명, URL, 자산, 권한 규칙, 기존 기록을 불러옵니다.
2. 대상 URL을 정규화하고 중복을 제거합니다.
3. 가용성, 적합성, 비용, 상호 링크, 계정, 약관, 중복, 신규/소유권 경로를 확인합니다.
4. CAPTCHA, 이메일, 전화, 2FA를 하나의 수동 작업 대기열로 모읍니다.
5. 인증 후 승인된 사실과 자산만 입력합니다.
6. 최종 작업 전에 비용, 브랜드, URL, 카테고리, 업로드, 동의, 중복 위험, 권한을 재확인합니다.
7. 정확한 응답, 시간, 결과 URL, 증거를 즉시 기록하고 감사를 실행합니다.

## 사용법

`submit-product-directories-v2-quality/`를 에이전트의 Skills 폴더에 복사하거나 폴더를 직접 참조하세요.

```text
$submit-product-directories-v2-quality로 디렉터리 URL을 검토하고 제품 제출
캠페인을 준비하세요. 먼저 적격성과 인증을 점검하고, 승인 없이 게시,
계정 생성, 약관 동의 또는 결제를 하지 마세요. 감사 가능한 기록과
수동 인증 대기열을 저장하세요.
```

```bash
python3 submit-product-directories-v2-quality/scripts/audit_submission_record.py path/to/record.md
python3 -m unittest discover -s submit-product-directories-v2-quality/tests
```

`submitted`에는 신뢰할 수 있는 접수 증거가, `published`에는 공개된 비미리보기 페이지가 필요합니다. 클릭이나 리디렉션만으로 성공을 추론하지 마세요.

## Flaq.ai 및 라이선스

[Flaq.ai](https://flaq.ai/)는 AI 에이전트와 프로덕션 앱에 이미지, 비디오, 음악, 언어 모델의 통합 접근을 제공합니다. 라이선스는 [LICENSE](LICENSE)를 참조하세요.
