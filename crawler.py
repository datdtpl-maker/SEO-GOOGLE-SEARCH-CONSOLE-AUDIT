import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor
import threading
import urllib3

# Tắt cảnh báo SSL không an toàn (nếu có cấu hình bỏ qua SSL)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SEOCrawler:
    def __init__(self, base_url, max_pages=500, max_workers=5):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.max_pages = max_pages
        self.max_workers = max_workers
        
        self.visited_urls = {} # URL -> details
        self.to_visit = set([base_url])
        self.url_parents = {} # URL -> parent_URL
        self.broken_links = [] # list of dicts: {url, status_code, parent_url}
        
        self.lock = threading.Lock()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; SEOAuditCrawler/1.0; +https://khaihoanderma.com/)'
        }

    def is_internal(self, url):
        return urlparse(url).netloc == self.domain

    def should_crawl(self, url):
        ignored_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico', '.pdf', '.zip', '.rar',
            '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.mp3', '.mp4', '.avi', '.mov',
            '.js', '.css', '.woff', '.woff2', '.ttf', '.xml', '.json'
        }
        parsed = urlparse(url)
        path = parsed.path.lower()
        for ext in ignored_extensions:
            if path.endswith(ext):
                return False
        return True


    def clean_url(self, url):
        # Loại bỏ phần hash (#anchor) để tránh quét trùng lặp
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    def crawl_page(self, url, parent_url=None):
        cleaned_url = self.clean_url(url)
        
        with self.lock:
            if cleaned_url in self.visited_urls and self.visited_urls[cleaned_url] != {"status": "processing"}:
                return
            if len(self.visited_urls) >= self.max_pages:
                return
            self.visited_urls[cleaned_url] = {"status": "processing"}


        # print(f"[Crawl] Đang quét: {cleaned_url}")
        
        try:
            response = requests.get(
                cleaned_url, 
                headers=self.headers, 
                timeout=10, 
                verify=False,
                allow_redirects=True
            )
            status_code = response.status_code
        except Exception as e:
            # Ghi nhận liên kết hỏng do không kết nối được
            with self.lock:
                self.visited_urls[cleaned_url] = {
                    "url": cleaned_url,
                    "status_code": 0,
                    "error": str(e),
                    "title": "Lỗi kết nối",
                    "meta_desc": "",
                    "h1_count": 0,
                    "missing_alts": 0,
                    "parent": parent_url
                }
                self.broken_links.append({
                    "url": cleaned_url,
                    "status_code": 0,
                    "error": str(e),
                    "parent": parent_url
                })
            return

        # Nếu gặp lỗi 404 hoặc lỗi máy chủ
        if status_code >= 400:
            with self.lock:
                self.visited_urls[cleaned_url] = {
                    "url": cleaned_url,
                    "status_code": status_code,
                    "title": f"Lỗi {status_code}",
                    "meta_desc": "",
                    "h1_count": 0,
                    "missing_alts": 0,
                    "parent": parent_url
                }
                self.broken_links.append({
                    "url": cleaned_url,
                    "status_code": status_code,
                    "error": f"HTTP {status_code}",
                    "parent": parent_url
                })
            return

        # Đọc On-page SEO
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type:
            with self.lock:
                self.visited_urls[cleaned_url] = {
                    "url": cleaned_url,
                    "status_code": status_code,
                    "title": "Định dạng không phải HTML",
                    "meta_desc": "",
                    "h1_count": 0,
                    "missing_alts": 0,
                    "parent": parent_url
                }
            return

        # Parse nội dung HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Lấy On-page SEO Info
        title = soup.find('title')
        title_text = title.text.strip() if title else "[Thiếu thẻ Title]"
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        desc_text = meta_desc.get('content', '').strip() if meta_desc else "[Thiếu thẻ Meta Description]"
        
        h1s = soup.find_all('h1')
        h1_count = len(h1s)
        
        # Tìm ảnh thiếu thẻ alt
        imgs = soup.find_all('img')
        missing_alts = 0
        for img in imgs:
            if not img.get('alt') or not img.get('alt').strip():
                # Bỏ qua các ảnh icon rất nhỏ
                width = img.get('width', '')
                height = img.get('height', '')
                if width.isdigit() and int(width) < 16:
                    continue
                missing_alts += 1

        with self.lock:
            self.visited_urls[cleaned_url] = {
                "url": cleaned_url,
                "status_code": status_code,
                "title": title_text,
                "meta_desc": desc_text,
                "h1_count": h1_count,
                "missing_alts": missing_alts,
                "parent": parent_url
            }

        # Tìm các link khác trong trang để tiếp tục quét
        links_to_queue = []
        for anchor in soup.find_all('a', href=True):
            href = anchor['href'].strip()
            if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
                continue
            
            absolute_url = urljoin(cleaned_url, href)
            # Chuẩn hóa URL
            absolute_url = self.clean_url(absolute_url)
            
            if self.is_internal(absolute_url) and self.should_crawl(absolute_url):
                with self.lock:
                    if absolute_url not in self.visited_urls and absolute_url not in self.to_visit:
                        self.to_visit.add(absolute_url)
                        self.url_parents[absolute_url] = cleaned_url
                        links_to_queue.append(absolute_url)
        
        return links_to_queue

    def run(self):
        print(f"Bắt đầu quét website: {self.base_url}")
        print(f"Cấu hình tối đa: {self.max_pages} trang, Số luồng: {self.max_workers}")
        
        # Quét trang chủ trước
        first_links = self.crawl_page(self.base_url)
        
        # Sử dụng ThreadPoolExecutor để quét đa luồng
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while True:
                with self.lock:
                    # Lấy các trang chưa được quét và chưa vượt quá giới hạn
                    to_crawl = [url for url in self.to_visit if url not in self.visited_urls or self.visited_urls[url] == {"status": "processing"}]
                    if not to_crawl or len(self.visited_urls) >= self.max_pages:
                        break
                
                # Tạo các job quét tệp
                futures = []
                for url in to_crawl[:self.max_workers * 2]:
                    # Đặt trạng thái đang xử lý để tránh luồng khác lấy trùng
                    with self.lock:
                        if url not in self.visited_urls:
                            self.visited_urls[url] = {"status": "processing"}
                    
                    # Tìm parent URL nếu có
                    parent = self.url_parents.get(url)
                    
                    futures.append(executor.submit(self.crawl_page, url, parent))
                
                # Đợi các luồng hoàn tất
                for future in futures:
                    try:
                        future.result()
                    except Exception as e:
                        print(f"Lỗi luồng: {e}")
                
                time.sleep(0.5)

        print(f"Quét hoàn tất. Đã quét: {len(self.visited_urls)} trang. Tìm thấy: {len(self.broken_links)} liên kết hỏng.")
        return {
            "visited_pages": self.visited_urls,
            "broken_links": self.broken_links
        }
