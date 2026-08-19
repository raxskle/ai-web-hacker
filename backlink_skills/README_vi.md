# Skill mã nguồn mở gửi backlink và danh bạ sản phẩm

> Được [Flaq.ai](https://flaq.ai/) tạo cho các tác nhân lập trình AI như Codex và Claude Code.

Quy trình có bằng chứng và có thể tiếp tục để gửi sản phẩm, phần mềm, startup, ứng dụng và website lên danh bạ sản phẩm cùng các kênh khám phá công khai. Skill hỗ trợ kiểm tra điều kiện, tránh gửi trùng, tuân thủ phạm vi ủy quyền, giữ bước xác minh thủ công, dùng dữ liệu trung thực và lưu kết quả có thể kiểm toán.

Danh bạ có thể tạo trích dẫn, lưu lượng giới thiệu hoặc backlink, nhưng dự án **không bảo đảm** vị trí liên kết, thuộc tính follow, phê duyệt, lập chỉ mục, lưu lượng hay thứ hạng.

**Ngôn ngữ:** [English](README_en.md) · [简体中文](README.md) · [繁體中文](README_tw.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [ไทย](README_th.md) · [Tiếng Việt](README_vi.md) · [Bahasa Indonesia](README_id.md) · [Español](README_es.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Italiano](README_it.md) · [Português](README_pt.md) · [Русский](README_ru.md) · [العربية](README_ar.md) · [हिन्दी](README_hi.md) · [Türkçe](README_tr.md) · [Nederlands](README_nl.md) · [Polski](README_pl.md)

## Phạm vi hỗ trợ

- Danh sách sản phẩm, phần mềm, công cụ AI, startup, công ty, ứng dụng và website
- `Request app`, đề xuất, yêu cầu quyền sở hữu danh sách và đăng ký nhà cung cấp
- Tạo tài khoản miễn phí hoặc hồ sơ công khai khi được phép
- Gửi blog, bài viết, tin tức, cộng đồng, email và biểu mẫu liên hệ
- Kiểm tra điều kiện, chi phí, liên kết đối ứng, tài khoản, trùng lặp và xác minh
- Theo dõi trạng thái bằng chứng và hồ sơ chiến dịch có thể tiếp tục

## Nguyên tắc an toàn

- Chỉ dùng thông tin đã xác minh về sản phẩm, công ty, người sáng lập, giá, liên hệ, quyền sở hữu và pháp lý.
- Không vượt CAPTCHA, Turnstile, 2FA, passkey hoặc xác minh email.
- Không thanh toán, bật gia hạn, thêm liên kết đối ứng, sửa website/DNS, tải tệp xác minh hay nhận quyền sở hữu nếu chưa được ủy quyền riêng.
- Không coi việc tạo tài khoản, lưu nháp, nhấp nút hay chuyển trang là đã xuất bản.
- Khi kết quả gửi cuối không rõ, phải điều tra trước khi thử lại để tránh trùng lặp.

## Quy trình

1. Nạp hồ sơ sản phẩm, mô tả, URL, tài sản, quy tắc ủy quyền và bản ghi đã duyệt.
2. Chuẩn hóa và loại bỏ URL mục tiêu trùng lặp.
3. Kiểm tra tính khả dụng, phù hợp, chi phí, liên kết đối ứng, tài khoản, điều khoản và trùng lặp.
4. Gom CAPTCHA, email, điện thoại và 2FA vào một hàng đợi thủ công.
5. Sau xác minh, chỉ điền dữ liệu và tài sản đã được duyệt.
6. Trước hành động cuối, kiểm tra lại chi phí, thương hiệu, URL, danh mục, tệp, thỏa thuận, rủi ro trùng và ủy quyền.
7. Ghi ngay phản hồi chính xác, thời gian, URL kết quả và bằng chứng, rồi kiểm toán hồ sơ.

## Cách dùng

Sao chép `submit-product-directories-v2-quality/` vào thư mục Skills của tác nhân hoặc tham chiếu trực tiếp thư mục này.

```text
Dùng $submit-product-directories-v2-quality để xem các URL danh bạ và chuẩn bị
chiến dịch gửi sản phẩm. Kiểm tra điều kiện và xác minh trước; không xuất bản,
tạo tài khoản, chấp nhận thỏa thuận hay thanh toán khi chưa được ủy quyền.
Lưu hồ sơ kiểm toán và một hàng đợi xác minh thủ công.
```

```bash
python3 submit-product-directories-v2-quality/scripts/audit_submission_record.py path/to/record.md
python3 -m unittest discover -s submit-product-directories-v2-quality/tests
```

`submitted` cần bằng chứng tiếp nhận đáng tin cậy; `published` cần trang công khai không phải bản xem trước. Không suy ra thành công chỉ từ cú nhấp hoặc chuyển hướng.

## Flaq.ai và giấy phép

[Flaq.ai](https://flaq.ai/) cung cấp quyền truy cập thống nhất vào mô hình hình ảnh, video, âm nhạc và ngôn ngữ cho tác nhân AI. Xem giấy phép tại [LICENSE](LICENSE).
