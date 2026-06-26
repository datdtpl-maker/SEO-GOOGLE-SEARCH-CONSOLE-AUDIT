import os
import sys
import config
from crawler import SEOCrawler
from gsc_client import GSCClient
from reporter import HTMLReporter

# Cấu hình mã hóa UTF-8 cho Windows console
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def print_header():

    print("=" * 60)
    print("      SEO CRAWLER & GOOGLE SEARCH CONSOLE AUDIT TOOL      ")
    print("=" * 60)
    print(f"Website mục tiêu: {config.SITE_URL}")
    print(f"Cấu hình tối đa: {config.MAX_CRAWL_PAGES} trang")
    print("=" * 60)

def main():
    print_header()

    # Bước 1: Khởi chạy Crawler quét lỗi 404 thực tế
    crawler = SEOCrawler(
        base_url=config.SITE_URL,
        max_pages=config.MAX_CRAWL_PAGES,
        max_workers=config.CRAWL_THREAD_COUNT
    )
    
    start_time = time_now()
    crawl_results = crawler.run()
    crawl_duration = time_now() - start_time
    print(f"Thời gian quét thực tế: {crawl_duration:.1f} giây.\n")

    # Bước 2: Khởi chạy Client lấy dữ liệu Google Search Console API
    gsc_client = GSCClient(
        credentials_file=config.CREDENTIALS_FILE,
        site_url=config.SITE_URL
    )
    
    gsc_data = None
    if gsc_client.connect():
        gsc_data = gsc_client.get_search_performance(days=30)
    else:
        print("\n[Lưu ý] Tiếp tục tạo báo cáo ngoại tuyến (Offline Report)...")

    # Bước 3: Gộp kết quả và xuất báo cáo HTML
    reporter = HTMLReporter(
        report_file=config.REPORT_FILE,
        site_url=config.SITE_URL
    )
    reporter.generate(crawl_results, gsc_data)

    print("\n" + "=" * 60)
    print("                    HOÀN TẤT QUÁ TRÌNH PHÂN TÍCH               ")
    print("=" * 60)
    print(f"Báo cáo của bạn tại: {os.path.abspath(config.REPORT_FILE)}")
    print("Hãy nhấp đúp chuột vào file trên để mở xem trên trình duyệt web.")
    print("=" * 60)

def time_now():
    import time
    return time.time()

if __name__ == "__main__":
    main()
