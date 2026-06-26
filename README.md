# SEO Auditor & Google Search Console Integration Tool

Công cụ tự động quét lỗi SEO On-page kết hợp phân tích hiệu suất tìm kiếm từ **Google Search Console (GSC) API**. Sau khi chạy, công cụ sẽ xuất ra một báo cáo Dashboard HTML đơn lẻ với giao diện **Glassmorphism** cao cấp, trực quan và hiện đại, giúp bạn dễ dàng theo dõi sức khỏe website cũng như đối soát hiệu suất tìm kiếm thực tế của từng URL.

---

## 🌟 Tính Năng Nổi Bật

- **Bộ Quét Website Đa Luồng (Multithreaded Crawler):**
  - Tự động thu thập và phân tích toàn bộ các liên kết nội bộ (Internal Links).
  - Lọc bỏ tài nguyên tĩnh (hình ảnh, CSS, JS, PDF) và bỏ qua liên kết ngoài (External Links) để tối ưu thời gian quét.
  - Kiểm tra mã trạng thái HTTP (200, 301, 302, 404, 500...) giúp nhanh chóng tìm thấy các trang bị lỗi hoặc redirect không hợp lý.
  - Đánh giá các tiêu chí SEO On-page: Title (độ dài, trùng lặp), Meta Description, Thẻ Header (H1, H2), hình ảnh thiếu thuộc tính `alt`.

- **Tích Hợp Google Search Console API:**
  - Tải dữ liệu hiệu suất của 30 ngày gần nhất từ GSC bao gồm: Clicks, Impressions, CTR và Vị trí trung bình (Average Position).
  - Đối khớp trực tiếp hiệu suất GSC với dữ liệu quét On-page của từng URL cụ thể để tìm ra cơ hội tối ưu hóa.

- **Báo Cáo Dashboard Glassmorphism Đẹp Mắt:**
  - Báo cáo được xuất ra dưới dạng **một file HTML duy nhất** dễ dàng chia sẻ.
  - Giao diện thiết kế theo phong cách Glassmorphism sang trọng, hỗ trợ Responsive đầy đủ trên cả điện thoại và máy tính.
  - Biểu đồ thống kê trực quan, các tab lọc nhanh lỗi 404, lỗi SEO On-page giúp dễ dàng khoanh vùng các trang cần tối ưu.

- **Chế Độ Tạo Dữ Liệu Mẫu (Offline Sample Mode):**
  - Cung cấp sẵn kịch bản giả lập giúp chạy thử nghiệm và kiểm tra giao diện báo cáo ngay lập tức mà không cần tài khoản GSC hoặc quét website thực tế.

---

## 📂 Cấu Trúc Thư Mục Dự Án

```text
gsc_seo_audit/
├── config.py                  # Cấu hình dự án (URL, luồng quét, tên file báo cáo...)
├── crawler.py                 # Bộ thu thập dữ liệu (quét website và check SEO On-page)
├── gsc_client.py              # Kết nối và tải dữ liệu từ Google Search Console API
├── reporter.py                # Xử lý dữ liệu và xuất báo cáo Dashboard HTML
├── run.py                     # File chạy chính phối hợp các module
├── generate_sample_data.py    # Kịch bản sinh dữ liệu mẫu để chạy thử nghiệm báo cáo
├── requirements.txt           # Danh sách thư viện Python cần cài đặt
├── .gitignore                 # Cấu hình loại bỏ tệp nhạy cảm khi đưa lên Git
└── README.md                  # Hướng dẫn sử dụng này
```

---

## 🛠️ Hướng Dẫn Cài Đặt & Cấu Hình

### 1. Chuẩn bị Môi trường
Dự án yêu cầu cài đặt **Python 3.8** trở lên. 

Thực hiện các bước sau tại thư mục dự án để thiết lập:

```bash
# 1. Tạo môi trường ảo (Khuyến nghị)
python -m venv venv

# 2. Kích hoạt môi trường ảo
# Trên Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Trên macOS/Linux:
source venv/bin/activate

# 3. Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt
```

### 2. Cấu Hình Google Search Console API (Service Account)
Để bảo mật và không yêu cầu đăng nhập trình duyệt mỗi lần quét, dự án sử dụng **Google Service Account (Tài khoản dịch vụ)** để kết nối với GSC API:

1. **Tạo Dự Án & Bật API:**
   - Truy cập [Google Cloud Console](https://console.cloud.google.com/).
   - Tạo một dự án mới hoặc chọn dự án hiện tại.
   - Đi tới mục **API & Services > Library**, tìm kiếm và bật **Google Search Console API**.

2. **Tạo Service Account & Tải Key:**
   - Đi tới mục **IAM & Admin > Service Accounts**.
   - Nhấp vào **Create Service Account**, nhập tên và hoàn thành.
   - Nhấp vào Service Account vừa tạo, chọn tab **Keys**, chọn **Add Key > Create new key** dạng **JSON**.
   - Tệp khóa JSON sẽ được tự động tải về máy của bạn.

3. **Cấu Hình Khóa Trong Dự Án:**
   - Đổi tên tệp khóa JSON đã tải về thành `service-account.json`.
   - Di chuyển tệp này vào thư mục gốc của dự án `gsc_seo_audit/` (tệp này đã được cấu hình trong `.gitignore` để tránh bị lộ ra công cộng).

4. **Cấp Quyền Đọc trên Google Search Console:**
   - Mở file `service-account.json` của bạn và sao chép địa chỉ email của Service Account (có dạng: `tên-account@dự-án.iam.gserviceaccount.com`).
   - Truy cập vào trang quản trị [Google Search Console](https://search.google.com/search-console).
   - Chọn trang web (Property) của bạn.
   - Đi tới **Settings > Users and permissions > Add user**.
   - Dán địa chỉ email Service Account vừa copy vào, chọn quyền **Full** hoặc **Restricted** (chỉ cần quyền đọc dữ liệu hiệu suất) rồi lưu lại.

---

## 🚀 Hướng Dẫn Sử Dụng

### Bước 1: Điều Chỉnh Cấu Hình
Mở file `config.py` và cập nhật các thông số cho phù hợp với website của bạn:
```python
# Cấu hình website cần quét (Lưu ý: Domain phải khớp chính xác với Property trên GSC)
SITE_URL = "https://example.com/"

# Số trang tối đa quét để tránh quá tải cho hosting
MAX_CRAWL_PAGES = 500

# Số luồng quét đồng thời
CRAWL_THREAD_COUNT = 5
```

### Bước 2: Chạy Công Cụ
Kích hoạt môi trường ảo và chạy lệnh sau để bắt đầu quét toàn bộ và tích hợp dữ liệu GSC:
```bash
python run.py
```
Sau khi tiến trình hoàn tất, báo cáo HTML mang tên `seo_audit_report.html` sẽ xuất hiện ở thư mục gốc. Bạn chỉ cần nhấp đúp để mở xem trên trình duyệt.

### Bước 3 (Tùy chọn): Chạy Thử Với Dữ Liệu Giả Lập
Nếu chưa cấu hình tài khoản GSC nhưng muốn kiểm tra ngay giao diện báo cáo HTML, bạn có thể chạy kịch bản tạo dữ liệu mẫu:
```bash
python generate_sample_data.py
```
Chương trình sẽ tự động tạo file `seo_audit_report.html` chứa dữ liệu SEO giả lập kết hợp biểu đồ GSC mẫu để bạn xem trước giao diện.

---

## 🔒 Cam Kết Bảo Mật
*   Tệp `service-account.json` chứa Private Key quản lý truy cập API của bạn **tuyệt đối không được đưa lên các dịch vụ lưu trữ mã nguồn mở công cộng** (như GitHub, GitLab).
*   File `.gitignore` đi kèm dự án đã loại trừ tệp khóa này cùng với các file HTML kết quả nhằm tránh rò rỉ dữ liệu vận hành thực tế của trang web.

---

*Chúc bạn tối ưu hóa SEO website thành công!*
