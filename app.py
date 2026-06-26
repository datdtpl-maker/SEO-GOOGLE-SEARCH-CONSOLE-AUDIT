import os
import sys
import time
import json
import base64
import threading
import queue
import webbrowser
import webview
from tkinter import filedialog, Tk

# Import core modules
import config
from crawler import SEOCrawler
from gsc_client import GSCClient
from reporter import HTMLReporter

def get_logo_base64():
    """Đọc logo.jpg từ các đường dẫn ưu tiên và chuyển sang Base64."""
    # Ưu tiên 1: Tìm logo.jpg nằm bên cạnh file chạy thực tế (cho phép người dùng ghi đè logo bên ngoài)
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        logo_path = os.path.join(exe_dir, "logo.jpg")
        if os.path.exists(logo_path):
            try:
                with open(logo_path, "rb") as img_file:
                    encoded = base64.b64encode(img_file.read()).decode('utf-8')
                    return f"data:image/jpeg;base64,{encoded}"
            except Exception:
                pass

    # Ưu tiên 2: Tìm logo.jpg được nhúng bên trong file .exe hoặc trong thư mục code
    if getattr(sys, 'frozen', False):
        # PyInstaller giải nén tài nguyên nhúng vào sys._MEIPASS
        project_dir = sys._MEIPASS
    else:
        project_dir = os.path.dirname(os.path.abspath(__file__))
        
    logo_path = os.path.join(project_dir, "logo.jpg")
    if os.path.exists(logo_path):
        try:
            with open(logo_path, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode('utf-8')
                return f"data:image/jpeg;base64,{encoded}"
        except Exception:
            pass
    return ""




# HTML/CSS/JS cho giao diện Cấu hình (phong cách Glassmorphism)
APP_UI_HTML = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Auditor & GSC Integration Tool</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #00adb5;
            --primary-hover: #088990;
            --bg-dark: #111424;
            --card-bg: rgba(255, 255, 255, 0.05);
            --border-color: rgba(255, 255, 255, 0.1);
            --text-color: #eeeeee;
            --text-muted: #8c90a6;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
        }

        body {
            background-color: var(--bg-dark);
            color: var(--text-color);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        /* Navigation Tabs Bar */
        .navbar {
            display: flex;
            background: rgba(17, 20, 36, 0.8);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border-color);
            padding: 0 20px;
            align-items: center;
            height: 60px;
            z-index: 100;
        }

        .logo {
            font-weight: 700;
            font-size: 16px;
            color: var(--primary);
            margin-right: 40px;
            letter-spacing: 0.5px;
        }

        .nav-links {
            display: flex;
            gap: 10px;
            height: 100%;
        }

        .nav-tab {
            display: flex;
            align-items: center;
            padding: 0 20px;
            color: var(--text-muted);
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            transition: all 0.3s ease;
            height: 100%;
        }

        .nav-tab:hover {
            color: var(--text-color);
        }

        .nav-tab.active {
            color: var(--primary);
            border-bottom-color: var(--primary);
        }

        .nav-tab.disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }

        /* Tab Content Panel */
        .tab-panel {
            flex: 1;
            padding: 25px;
            display: none;
            overflow-y: auto;
            position: relative;
        }

        .tab-panel.active {
            display: flex;
            flex-direction: column;
        }

        /* Config Form Styling */
        .container {
            max-width: 900px;
            width: 100%;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .header-section {
            margin-bottom: 10px;
        }

        .header-section h1 {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .header-section p {
            color: var(--text-muted);
            font-size: 14px;
        }

        .glass-card {
            background: var(--card-bg);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        }

        .form-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .form-group-row {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        label {
            font-weight: 600;
            font-size: 13px;
            color: var(--text-color);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        input[type="text"] {
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 12px;
            color: var(--text-color);
            font-size: 14px;
            width: 100%;
            transition: border-color 0.3s;
        }

        input[type="text"]:focus {
            outline: none;
            border-color: var(--primary);
        }

        .btn {
            background-color: var(--primary);
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .btn:hover:not(:disabled) {
            background-color: var(--primary-hover);
        }

        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .btn-secondary {
            background-color: rgba(255, 255, 255, 0.1);
            color: var(--text-color);
        }

        .btn-secondary:hover:not(:disabled) {
            background-color: rgba(255, 255, 255, 0.2);
        }

        /* Sliders */
        .slider-container {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .slider-container input[type="range"] {
            flex: 1;
            accent-color: var(--primary);
            height: 6px;
            border-radius: 3px;
            cursor: pointer;
        }

        .slider-value {
            font-weight: 600;
            min-width: 80px;
            text-align: right;
            color: var(--primary);
        }

        /* Log Console Display */
        .console-container {
            display: flex;
            flex-direction: column;
            gap: 10px;
            flex: 1;
            min-height: 250px;
        }

        .console-box {
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 15px;
            font-family: 'Consolas', monospace;
            font-size: 12.5px;
            color: #a9b7c6;
            overflow-y: auto;
            flex: 1;
            white-space: pre-wrap;
            line-height: 1.5;
        }

        /* Iframe Panel */
        #iframe-panel {
            padding: 0;
            width: 100%;
            height: calc(100vh - 60px);
        }

        iframe {
            width: 100%;
            height: 100%;
            border: none;
            background-color: var(--bg-dark);
        }

        /* Spinner Loading */
        .spinner {
            border: 3px solid rgba(255, 255, 255, 0.1);
            width: 16px;
            height: 16px;
            border-radius: 50%;
            border-left-color: #ffffff;
            animation: spin 1s linear infinite;
            display: none;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>

    <!-- Tab Bar -->
    <div class="navbar">
        <div class="logo" style="display: flex; align-items: center; gap: 10px;">
            <img id="logo-img" src="" style="width: 32px; height: 32px; border-radius: 50%; display: none; object-fit: cover; border: 1.5px solid var(--primary);">
            <span id="logo-text">SEO AUDITOR & GSC</span>
        </div>
        <div class="nav-links">
            <div id="tab-btn-config" class="nav-tab active" onclick="switchTab('config-panel')">Cấu hình & Quét</div>
            <div id="tab-btn-report" class="nav-tab disabled" onclick="switchTab('iframe-panel')">Báo cáo kết quả</div>
        </div>
    </div>

    <!-- Panel 1: Cấu hình và Quét -->
    <div id="config-panel" class="tab-panel active">
        <div class="container">
            <div class="header-section">
                <h1>Hệ Thống Phân Tích SEO On-page & Google Search Console</h1>
                <p>Quét các liên kết hỏng, kiểm tra thẻ tiêu đề và tích hợp dữ liệu Organic Search Performance từ GSC.</p>
            </div>

            <!-- Form Cấu Hình -->
            <div class="glass-card form-grid">
                <div class="form-group">
                    <label for="site-url">Website URL:</label>
                    <input type="text" id="site-url" placeholder="https://example.com/">
                </div>

                <div class="form-group">
                    <label for="json-path">Google Service Account Key (JSON):</label>
                    <div class="form-group-row">
                        <input type="text" id="json-path" placeholder="Đường dẫn đến file service-account.json">
                        <button class="btn btn-secondary" id="btn-browse" onclick="browseJsonFile()">Browse...</button>
                    </div>
                </div>

                <div class="form-group">
                    <label>Giới hạn trang quét (Max Pages):</label>
                    <div class="slider-container">
                        <input type="range" id="max-pages" min="10" max="2000" step="10" oninput="updateSliderLabel('max-pages-val', this.value)">
                        <span id="max-pages-val" class="slider-value">500 trang</span>
                    </div>
                </div>

                <div class="form-group">
                    <label>Số luồng quét (Threads):</label>
                    <div class="slider-container">
                        <input type="range" id="threads" min="1" max="10" step="1" oninput="updateSliderLabel('threads-val', this.value)">
                        <span id="threads-val" class="slider-value">5 luồng</span>
                    </div>
                </div>
            </div>

            <!-- Nút Action & Log Console -->
            <div class="glass-card console-container">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <label>Bảng Tiến Trình Hệ Thống (Log Console):</label>
                    <button class="btn" id="btn-start" onclick="startAudit()">
                        <div class="spinner" id="btn-spinner"></div>
                        <span id="btn-text">Bắt đầu quét SEO & GSC</span>
                    </button>
                </div>
                <div class="console-box" id="console-output">Chưa khởi chạy tiến trình quét...</div>
            </div>
        </div>
    </div>

    <!-- Panel 2: Iframe hiển thị Báo cáo -->
    <div id="iframe-panel" class="tab-panel">
        <iframe id="report-iframe" src="about:blank"></iframe>
    </div>

    <script>
        // Cấu hình ban đầu từ Python tải lên
        window.addEventListener('pywebviewready', function() {
            // Tải cấu hình mặc định từ Python gửi xuống
            window.pywebview.api.get_initial_config().then(function(res) {
                document.getElementById('site-url').value = res.site_url;
                document.getElementById('json-path').value = res.credentials_file;
                
                document.getElementById('max-pages').value = res.max_pages;
                document.getElementById('max-pages-val').innerText = res.max_pages + " trang";
                
                document.getElementById('threads').value = res.threads;
                document.getElementById('threads-val').innerText = res.threads + " luồng";
                
                if (res.logo_b64) {
                    const logoEl = document.getElementById('logo-img');
                    logoEl.src = res.logo_b64;
                    logoEl.style.display = 'block';
                    document.getElementById('logo-text').innerText = 'KHẢI HOÀN DERMA';
                }
            });
        });

        function updateSliderLabel(id, val) {
            const suffix = id.includes('pages') ? ' trang' : ' luồng';
            document.getElementById(id).innerText = val + suffix;
        }

        function switchTab(panelId) {
            // Kiểm tra nếu tab report bị khóa
            if (panelId === 'iframe-panel' && document.getElementById('tab-btn-report').classList.contains('disabled')) {
                return;
            }

            // Chuyển active class cho nút tab
            document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
            if (panelId === 'config-panel') {
                document.getElementById('tab-btn-config').classList.add('active');
            } else {
                document.getElementById('tab-btn-report').classList.add('active');
            }

            // Chuyển active class cho nội dung panel
            document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
            document.getElementById(panelId).classList.add('active');
        }

        function browseJsonFile() {
            window.pywebview.api.browse_json().then(function(filePath) {
                if (filePath) {
                    document.getElementById('json-path').value = filePath;
                }
            });
        }

        function appendLog(message) {
            const consoleBox = document.getElementById('console-output');
            if (consoleBox.innerText === "Chưa khởi chạy tiến trình quét...") {
                consoleBox.innerText = "";
            }
            consoleBox.innerText += message;
            consoleBox.scrollTop = consoleBox.scrollHeight;
        }

        function startAudit() {
            const url = document.getElementById('site-url').value.trim();
            const jsonPath = document.getElementById('json-path').value.strip ? document.getElementById('json-path').value.strip() : document.getElementById('json-path').value;
            const maxPages = parseInt(document.getElementById('max-pages').value);
            const threads = parseInt(document.getElementById('threads').value);

            if (!url.startsWith('http://') && !url.startsWith('https://')) {
                alert("Website URL phải bắt đầu bằng http:// hoặc https://");
                return;
            }

            // Khóa giao diện
            document.getElementById('btn-start').disabled = true;
            document.getElementById('btn-browse').disabled = true;
            document.getElementById('site-url').disabled = true;
            document.getElementById('json-path').disabled = true;
            document.getElementById('max-pages').disabled = true;
            document.getElementById('threads').disabled = true;
            document.getElementById('btn-spinner').style.display = 'block';
            document.getElementById('btn-text').innerText = 'Đang quét dữ liệu...';
            document.getElementById('tab-btn-report').classList.add('disabled');

            // Reset log console
            document.getElementById('console-output').innerText = "";

            // Gọi Python thực thi
            window.pywebview.api.start_scan(url, jsonPath, maxPages, threads);
        }

        function scanFinished(success, resultPathOrError) {
            // Mở khóa giao diện
            document.getElementById('btn-start').disabled = false;
            document.getElementById('btn-browse').disabled = false;
            document.getElementById('site-url').disabled = false;
            document.getElementById('json-path').disabled = false;
            document.getElementById('max-pages').disabled = false;
            document.getElementById('threads').disabled = false;
            document.getElementById('btn-spinner').style.display = 'none';
            document.getElementById('btn-text').innerText = 'Bắt đầu quét SEO & GSC';

            if (success) {
                // Kích hoạt tab báo cáo kết quả và gán src cho iframe
                const tabReport = document.getElementById('tab-btn-report');
                tabReport.classList.remove('disabled');
                
                document.getElementById('report-iframe').src = resultPathOrError;
                
                // Chuyển hướng tab sang báo cáo
                switchTab('iframe-panel');
            } else {
                alert("Có lỗi xảy ra khi quét: " + resultPathOrError);
            }
        }
    </script>
</body>
</html>
"""

class WebviewRedirector:
    """Định hướng log từ sys.stdout trực tiếp vào Webview console."""
    def __init__(self, window):
        self.window = window

    def write(self, string):
        if string:
            # Đẩy log vào giao diện HTML bằng cách chạy Javascript
            self.window.evaluate_js(f"appendLog({json.dumps(string)})")

    def flush(self):
        pass

class WebviewAPI:
    """Các API cung cấp cho phía Javascript gọi xuống Python."""
    def __init__(self):
        self.window = None

    def set_window(self, window):
        self.window = window

    def get_initial_config(self):
        """Trả về các cấu hình mặc định từ config.py."""
        logo_b64 = get_logo_base64()
        return {
            "site_url": config.SITE_URL,
            "credentials_file": os.path.abspath(config.CREDENTIALS_FILE) if os.path.exists(config.CREDENTIALS_FILE) else config.CREDENTIALS_FILE,
            "max_pages": config.MAX_CRAWL_PAGES,
            "threads": config.CRAWL_THREAD_COUNT,
            "logo_b64": logo_b64
        }

    def browse_json(self):
        """Mở File Dialog Windows để chọn file JSON."""
        # Ẩn cửa sổ root Tkinter phụ
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        file_path = filedialog.askopenfilename(
            title="Chọn file service-account.json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        root.destroy()
        return file_path if file_path else ""

    def start_scan(self, url, json_path, max_pages, threads):
        """Chạy quét trong một luồng nền để tránh block Webview UI."""
        scan_thread = threading.Thread(
            target=self._run_scan_thread,
            args=(url, json_path, max_pages, threads)
        )
        scan_thread.daemon = True
        scan_thread.start()

    def _run_scan_thread(self, url, json_path, max_pages, threads):
        try:
            start_time = time.time()
            
            print("=" * 60)
            print("      SEO CRAWLER & GOOGLE SEARCH CONSOLE AUDIT TOOL      ")
            print("=" * 60)
            print(f"Website mục tiêu: {url}")
            print(f"Cấu hình tối đa: {max_pages} trang")
            print(f"Số luồng quét: {threads} luồng")
            print(f"File Credentials: {json_path}")
            print("=" * 60 + "\n")

            # 1. Chạy Crawler
            print("[1/3] Đang khởi chạy Bộ quét dữ liệu đa luồng (Crawler)...")
            crawler = SEOCrawler(
                base_url=url,
                max_pages=max_pages,
                max_workers=threads
            )
            crawl_results = crawler.run()
            crawl_duration = time.time() - start_time
            print(f"-> Quá trình quét hoàn tất trong {crawl_duration:.1f} giây.\n")

            # 2. Truy xuất Search Console API
            print("[2/3] Đang kết nối tới Google Search Console API...")
            gsc_client = GSCClient(
                credentials_file=json_path,
                site_url=url
            )
            
            gsc_data = None
            if gsc_client.connect():
                print("-> Kết nối API GSC thành công. Đang tải dữ liệu hiệu suất 30 ngày qua...")
                gsc_data = gsc_client.get_search_performance(days=30)
                if gsc_data:
                    print(f"-> Tải thành công dữ liệu hiệu suất cho {len(gsc_data)} URL từ GSC.")
                else:
                    print("-> Không có dữ liệu hiệu suất hoặc không tìm thấy URL nào khớp.")
            else:
                print("-> [Cảnh Báo] Không thể kết nối tới Google Search Console API.")
                print("   Vui lòng kiểm tra lại file service-account.json hoặc quyền truy cập của Service Account trong GSC.")
                print("   Chương trình sẽ tự động tiếp tục tạo báo cáo ngoại tuyến (Offline Report)...\n")

            # 3. Xuất báo cáo HTML
            print("[3/3] Đang biên dịch và kết xuất Báo cáo HTML Dashboard...")
            reporter = HTMLReporter(
                report_file=config.REPORT_FILE,
                site_url=url
            )
            reporter.generate(crawl_results, gsc_data)
            
            total_duration = time.time() - start_time
            report_abspath = os.path.abspath(config.REPORT_FILE)
            
            print("\n" + "=" * 60)
            print("                    HOÀN TẤT TIẾN TRÌNH QUÉT               ")
            print("=" * 60)
            print(f"Tổng thời gian xử lý: {total_duration:.1f} giây.")
            print(f"Báo cáo xuất tại: {report_abspath}")
            print("=" * 60 + "\n")
            
            # Gửi thông tin về cho JS cập nhật UI (Chuyển sang định dạng URI chuẩn hóa)
            from pathlib import Path
            report_uri = Path(report_abspath).as_uri()
            self.window.evaluate_js(f"scanFinished(true, {json.dumps(report_uri)})")

        except Exception as e:
            print(f"\n[LỖI HỆ THỐNG] Đã xảy ra lỗi trong quá trình quét: {str(e)}")
            import traceback
            traceback.print_exc()
            self.window.evaluate_js(f"scanFinished(false, {json.dumps(str(e))})")

def main():
    # 1. Tạo file HTML tạm phục vụ giao diện cấu hình (cùng Origin file:/// giúp nhúng iframe mượt mà)
    ui_path = os.path.abspath("app_ui.html")
    with open(ui_path, "w", encoding="utf-8") as f:
        f.write(APP_UI_HTML)

    # 2. Cấu hình API và khởi tạo pywebview (Chuyển đường dẫn sang URI chuẩn hóa cho Edge)
    from pathlib import Path
    ui_url = Path(ui_path).as_uri()

    api = WebviewAPI()
    window = webview.create_window(
        title="SEO Auditor & GSC Integration Dashboard",
        url=ui_url,
        width=1200,
        height=800,
        resizable=True,
        js_api=api
    )
    api.set_window(window)

    # 3. Redirect stdout & stderr về log console của Webview
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = WebviewRedirector(window)
    sys.stderr = WebviewRedirector(window)

    try:
        # Chạy Webview GUI
        webview.start()
    finally:
        # Dọn dẹp: Trả lại stdout & stderr nguyên bản và xóa file UI tạm khi tắt ứng dụng
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        if os.path.exists(ui_path):
            try:
                os.remove(ui_path)
            except Exception:
                pass

if __name__ == "__main__":
    main()
