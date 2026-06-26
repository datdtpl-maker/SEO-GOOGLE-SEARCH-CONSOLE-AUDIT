import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

class GSCClient:
    def __init__(self, credentials_file, site_url):
        self.credentials_file = credentials_file
        # Google Search Console API yêu cầu định dạng siteUrl chính xác (phải khớp với loại tài sản trong GSC, ví dụ sc-domain:domain.com hoặc https://domain.com/)
        self.site_url = site_url
        self.credentials = None
        self.service = None

    def connect(self):
        if not os.path.exists(self.credentials_file):
            print(f"[Cảnh báo] Không tìm thấy file xác thực '{self.credentials_file}'.")
            print("Chương trình sẽ chạy ở chế độ Quét Ngoại Tuyến (Offline Crawler) không có số liệu Google Search Console.")
            return False

        try:
            scopes = ['https://www.googleapis.com/auth/webmasters.readonly']
            self.credentials = service_account.Credentials.from_service_account_file(
                self.credentials_file, 
                scopes=scopes
            )
            # Khởi tạo service kết nối tới Webmasters API v3 (Search Console)
            self.service = build('webmasters', 'v3', credentials=self.credentials)
            print("[Thành công] Kết nối API Google Search Console thành công!")
            return True
        except Exception as e:
            print(f"[Lỗi] Không thể kết nối API Google Search Console: {e}")
            print("Vui lòng kiểm tra lại file key JSON và cấu hình quyền hạn trong Google Search Console.")
            return False

    def get_search_performance(self, days=30):
        if not self.service:
            return None

        # Tính toán khoảng thời gian
        end_date = datetime.now() - timedelta(days=3) # GSC dữ liệu thường trễ 2-3 ngày
        start_date = end_date - timedelta(days=days)
        
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        print(f"Đang tải số liệu hiệu suất GSC từ {start_date_str} đến {end_date_str}...")

        # 1. Lấy dữ liệu theo Trang (Pages)
        page_data = {}
        try:
            request_body = {
                'startDate': start_date_str,
                'endDate': end_date_str,
                'dimensions': ['page'],
                'rowLimit': 2000
            }
            response = self.service.searchanalytics().query(
                siteUrl=self.site_url, 
                body=request_body
            ).execute()

            if 'rows' in response:
                for row in response['rows']:
                    page_url = row['keys'][0]
                    page_data[page_url] = {
                        "clicks": row['clicks'],
                        "impressions": row['impressions'],
                        "ctr": round(row['ctr'] * 100, 2),
                        "position": round(row['position'], 1)
                    }
        except Exception as e:
            print(f"[Lỗi] Không thể tải dữ liệu hiệu suất trang: {e}")

        # 2. Lấy dữ liệu theo Từ khóa (Queries)
        query_data = []
        try:
            request_body = {
                'startDate': start_date_str,
                'endDate': end_date_str,
                'dimensions': ['query'],
                'rowLimit': 100
            }
            response = self.service.searchanalytics().query(
                siteUrl=self.site_url, 
                body=request_body
            ).execute()

            if 'rows' in response:
                for row in response['rows']:
                    query_data.append({
                        "query": row['keys'][0],
                        "clicks": row['clicks'],
                        "impressions": row['impressions'],
                        "ctr": round(row['ctr'] * 100, 2),
                        "position": round(row['position'], 1)
                    })
        except Exception as e:
            print(f"[Lỗi] Không thể tải dữ liệu từ khóa hàng đầu: {e}")

        # 3. Lấy thông tin sơ đồ trang web (Sitemaps)
        sitemaps_data = []
        try:
            response = self.service.sitemaps().list(siteUrl=self.site_url).execute()
            if 'sitemap' in response:
                for map_info in response['sitemap']:
                    sitemaps_data.append({
                        "path": map_info.get('path'),
                        "last_submitted": map_info.get('lastSubmitted'),
                        "last_downloaded": map_info.get('lastDownloaded'),
                        "warnings": map_info.get('warnings', 0),
                        "errors": map_info.get('errors', 0)
                    })
        except Exception as e:
            print(f"[Lỗi] Không thể tải thông tin sitemaps: {e}")

        return {
            "pages": page_data,
            "queries": query_data,
            "sitemaps": sitemaps_data
        }
