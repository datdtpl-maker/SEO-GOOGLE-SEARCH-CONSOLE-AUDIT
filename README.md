# SEO Auditor & Google Search Console Integration Tool

Công cụ tự động quét lỗi SEO On-page kết hợp phân tích hiệu suất tìm kiếm từ **Google Search Console (GSC) API**. Dự án hỗ trợ cả giao diện dòng lệnh (CLI), giao diện đồ họa hiện đại (GUI) và file chạy độc lập `.exe` giúp bạn thực hiện kiểm tra dễ dàng bằng một cú nhấp chuột trên máy tính Windows.

---

## 🌟 Tính Năng Nổi Bật

- **Giao Diện Đồ Họa Hiện Đại (GUI):**
  - Giao diện Dark Mode đẹp mắt, hỗ trợ người dùng nhập Website URL, lựa chọn tệp key GSC qua cửa sổ chọn file của Windows (File Dialog), điều chỉnh nhanh số trang tối đa và số luồng quét bằng thanh trượt (Slider).
  - Có khung hiển thị tiến trình (Log Console) trực tiếp thời gian thực, giúp bạn nắm bắt tức thì quá trình quét.
  - Hỗ trợ nút **Mở Báo Cáo HTML (Open Report)** để mở ngay dashboard kết quả trên trình duyệt sau khi quét xong.

- **Đóng Gói File Chạy Độc Lập (.exe):**
  - Tích hợp tệp `SEO_GSC_Auditor.exe` trong thư mục `dist/` chạy trực tiếp trên Windows mà không cần cài đặt Python hay bất kỳ thư viện bổ sung nào.

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
  - Giao diện thiết kế theo phong cách Glassmorphism sang trọng, hỗ trợ Responsive đầy đủ.
  - Biểu đồ thống kê trực quan, các tab lọc nhanh lỗi 404, lỗi SEO On-page giúp dễ dàng khoanh vùng các trang cần tối ưu.

- **Chế Độ Tạo Dữ Liệu Mẫu (Offline Sample Mode):**
  - Cung cấp sẵn kịch bản giả lập giúp chạy thử nghiệm và kiểm tra giao diện báo cáo ngay lập tức mà không cần tài khoản GSC hoặc quét website thực tế.

---

## 📂 Cấu Trúc Thư Mục Dự Án

```text
gsc_seo_audit/
├── gui.py                     # Giao diện đồ họa (GUI) của công cụ chạy trực tiếp bằng Python
├── run.py                     # File chạy chính phối hợp các module (Giao diện dòng lệnh - CLI)
├── config.py                  # Cấu hình dự án (URL, luồng quét, tên file báo cáo...)
├── crawler.py                 # Bộ thu thập dữ liệu (quét website và check SEO On-page)
├── gsc_client.py              # Kết nối và tải dữ liệu từ Google Search Console API
├── reporter.py                # Xử lý dữ liệu và xuất báo cáo Dashboard HTML
├── generate_sample_data.py    # Kịch bản sinh dữ liệu mẫu để chạy thử nghiệm báo cáo
├── requirements.txt           # Danh sách thư viện Python cần cài đặt
├── .gitignore                 # Cấu hình loại bỏ tệp nhạy cảm và file build khi đưa lên Git
├── README.md                  # Hướng dẫn sử dụng này
└── dist/
    └── SEO_GSC_Auditor.exe    # Ứng dụng chạy độc lập trên Windows (chạy ngay không cần cài đặt gì thêm)
```

---

## 🛠️ Hướng Dẫn Cài Đặt & Chạy Bằng Mã Nguồn Python

### 1. Chuẩn bị Môi trường
Dự án yêu cầu cài đặt **Python 3.8** trở lên. Thực hiện thiết lập môi trường:

```bash
# 1. Tạo môi trường ảo (Khuyến nghị)
python -m venv venv

# 2. Kích hoạt môi trường ảo
# Trên Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Trên macOS/Linux:
source venv/bin/activate

# 3. Cài đặt các thư viện phụ thuộc (bao gồm cả customtkinter phục vụ GUI)
pip install -r requirements.txt
pip install customtkinter
```

### 2. Cấu Hình Google Search Console API (Service Account)
Để bảo mật và không yêu cầu đăng nhập trình duyệt mỗi lần quét, dự án sử dụng **Google Service Account (Tài khoản dịch vụ)** để kết nối với GSC API:

1. **Tạo Dự Án & Bật API:**
   - Truy cập [Google Cloud Console](https://console.cloud.google.com/).
   - Tạo dự án mới và bật **Google Search Console API**.
2. **Tạo Service Account & Tải Key:**
   - Đi tới mục **IAM & Admin > Service Accounts > Create Service Account**.
   - Sau khi tạo, nhấn vào Service Account đó, chọn tab **Keys > Add Key > Create new key** dạng **JSON**.
   - Tệp khóa JSON tải về máy hãy đổi tên thành `service-account.json` và di chuyển vào thư mục gốc của dự án (tệp này được bỏ qua trong `.gitignore` để bảo mật).
3. **Cấp Quyền trên Google Search Console:**
   - Copy địa chỉ email của Service Account (dạng: `tên-account@dự-án.iam.gserviceaccount.com`).
   - Vào [Google Search Console](https://search.google.com/search-console) chọn Property của bạn.
   - Đi tới **Settings > Users and permissions > Add user**, dán email vào và cấp quyền đọc (Viewer/Full).

---

## 🚀 Hướng Dẫn Sử Dụng

### Cách 1: Sử Dụng Ứng Dụng File Chạy Độc Lập `.exe` (Khuyên dùng cho người dùng cuối)
1. Truy cập vào thư mục `dist/` và nhấp đúp chuột vào file `SEO_GSC_Auditor.exe` để mở ứng dụng.
2. Trên giao diện hiện lên:
   * **Website URL:** Nhập trang web bạn muốn quét.
   * **Service Account Key:** Bấm nút **Browse...** để chọn file khóa `service-account.json` bạn đã chuẩn bị.
   * **Sliders:** Kéo chỉnh số trang tối đa và số luồng quét.
   * Bấm **Bắt đầu quét SEO & GSC (Start Audit)** để chương trình tự động chạy.
3. Khi hoàn tất, một thông báo thành công xuất hiện và chương trình sẽ tự động mở báo cáo `seo_audit_report.html` trên trình duyệt web của bạn.

### Cách 2: Chạy Giao Diện Đồ Họa (GUI) Bằng Python
Trong môi trường ảo của bạn, chạy lệnh sau:
```bash
python gui.py
```
Giao diện đồ họa tương tự như file `.exe` sẽ hiện lên giúp bạn thao tác cấu hình trực quan.

### Cách 3: Chạy Giao Diện Dòng Lệnh (CLI)
Cấu hình các thông số trong file `config.py` sau đó chạy lệnh:
```bash
python run.py
```

### Chạy Thử Với Dữ Liệu Giả Lập (Không cần kết nối API GSC)
Để xem trước giao diện báo cáo Dashboard HTML mà không cần chuẩn bị API GSC, hãy chạy:
```bash
python generate_sample_data.py
```
File báo cáo demo `seo_audit_report.html` sẽ tự động được sinh ra và mở trên trình duyệt.

---

## 🔒 Cam Kết Bảo Mật
*   Tệp `service-account.json` chứa Private Key quản lý truy cập API của bạn **tuyệt đối không được đưa lên các dịch vụ lưu trữ mã nguồn mở công cộng** (như GitHub).
*   File `.gitignore` đi kèm dự án đã loại trừ tệp khóa này cùng với các thư mục build tạm, file `.exe` kết quả và các file HTML kết quả nhằm tránh rò rỉ dữ liệu vận hành thực tế của trang web.

---

*Chúc bạn tối ưu hóa SEO website thành công!*
