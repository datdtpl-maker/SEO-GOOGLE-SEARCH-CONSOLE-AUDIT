import os

# Cấu hình website cần quét
SITE_URL = "https://khaihoanderma.com/"

# Cấu hình Google Search Console API
# File JSON này bạn tải về từ Google Cloud Console và đặt vào cùng thư mục dự án
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "service-account.json")

# Cấu hình Crawler
# Số trang tối đa quét để tránh quá tải cho hosting của bạn (mặc định là 1000 trang)
MAX_CRAWL_PAGES = 1000

# Số luồng quét đồng thời (tối ưu từ 3 đến 8 để tránh bị chặn IP)
CRAWL_THREAD_COUNT = 5

# Tên file báo cáo xuất ra
REPORT_FILE = "seo_audit_report.html"
