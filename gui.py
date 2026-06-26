import os
import sys
import time
import threading
import webbrowser
import queue
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Import core modules
import config
from crawler import SEOCrawler
from gsc_client import GSCClient
from reporter import HTMLReporter

# Cấu hình giao diện CustomTkinter
ctk.set_appearance_mode("dark")  # Chế độ tối mặc định
ctk.set_default_color_theme("blue")  # Màu chủ đạo xanh dương

class TextRedirector:
    """Chuyển hướng sys.stdout vào widget CTkTextbox một cách an sau."""
    def __init__(self, text_widget, log_queue):
        self.text_widget = text_widget
        self.log_queue = log_queue

    def write(self, string):
        if string:
            self.log_queue.put(string)

    def flush(self):
        pass

class SEOAuditorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Cấu hình cửa sổ chính
        self.title("SEO Auditor & GSC Integration Tool")
        self.geometry("820x680")
        self.minsize(750, 600)

        # Cấu hình lưới grid hệ thống
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Biến cấu hình giao diện
        self.url_var = ctk.StringVar(value=config.SITE_URL)
        self.json_var = ctk.StringVar(value=os.path.abspath(config.CREDENTIALS_FILE) if os.path.exists(config.CREDENTIALS_FILE) else config.CREDENTIALS_FILE)
        self.max_pages_var = ctk.IntVar(value=config.MAX_CRAWL_PAGES)
        self.threads_var = ctk.IntVar(value=config.CRAWL_THREAD_COUNT)
        self.is_running = False

        # Queue để truyền log an toàn giữa các luồng
        self.log_queue = queue.Queue()

        # Tạo các widget
        self.create_widgets()

        # Bắt đầu kiểm tra hàng đợi log định kỳ
        self.update_log_from_queue()

        # Chuyển hướng stdout & stderr
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = TextRedirector(self.log_textbox, self.log_queue)
        sys.stderr = TextRedirector(self.log_textbox, self.log_queue)

    def create_widgets(self):
        # 1. Header Frame
        header_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1a1a2e")
        header_frame.grid(row=0, column=0, padx=15, pady=10, sticky="ew")
        
        header_label = ctk.CTkLabel(
            header_frame, 
            text="SEO AUDITOR & GOOGLE SEARCH CONSOLE AUDIT TOOL", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#00adb5"
        )
        header_label.pack(padx=20, pady=15)

        # 2. Configuration Frame
        config_frame = ctk.CTkFrame(self, corner_radius=10)
        config_frame.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        config_frame.grid_columnconfigure(1, weight=1)

        # Target URL Input
        ctk.CTkLabel(config_frame, text="Website URL:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.url_entry = ctk.CTkEntry(config_frame, textvariable=self.url_var, placeholder_text="https://example.com/")
        self.url_entry.grid(row=0, column=1, columnspan=2, padx=(0, 15), pady=10, sticky="ew")

        # Credentials JSON Input
        ctk.CTkLabel(config_frame, text="Service Account Key (JSON):", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.json_entry = ctk.CTkEntry(config_frame, textvariable=self.json_var, placeholder_text="Đường dẫn tới file service-account.json")
        self.json_entry.grid(row=1, column=1, padx=(0, 10), pady=10, sticky="ew")
        
        self.browse_btn = ctk.CTkButton(config_frame, text="Browse...", width=90, command=self.browse_json)
        self.browse_btn.grid(row=1, column=2, padx=(0, 15), pady=10, sticky="e")

        # Max Pages Slider
        ctk.CTkLabel(config_frame, text="Giới hạn trang quét (Max Pages):", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=15, pady=10, sticky="w")
        self.max_pages_slider = ctk.CTkSlider(config_frame, from_=10, to=2000, number_of_steps=199, command=self.update_max_pages_label)
        self.max_pages_slider.set(self.max_pages_var.get())
        self.max_pages_slider.grid(row=2, column=1, padx=(0, 10), pady=10, sticky="ew")
        
        self.max_pages_label = ctk.CTkLabel(config_frame, text=f"{self.max_pages_var.get()} trang", width=90)
        self.max_pages_label.grid(row=2, column=2, padx=(0, 15), pady=10, sticky="e")

        # Thread Count Slider
        ctk.CTkLabel(config_frame, text="Số luồng quét (Threads):", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, padx=15, pady=10, sticky="w")
        self.thread_slider = ctk.CTkSlider(config_frame, from_=1, to=10, number_of_steps=9, command=self.update_threads_label)
        self.thread_slider.set(self.threads_var.get())
        self.thread_slider.grid(row=3, column=1, padx=(0, 10), pady=10, sticky="ew")
        
        self.threads_label = ctk.CTkLabel(config_frame, text=f"{self.threads_var.get()} luồng", width=90)
        self.threads_label.grid(row=3, column=2, padx=(0, 15), pady=10, sticky="e")

        # 3. Log Console Frame
        log_frame = ctk.CTkFrame(self, corner_radius=10)
        log_frame.grid(row=2, column=0, padx=15, pady=10, sticky="nsew")
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(log_frame, text="Tiến Trình Chạy Hệ Thống (Log Console):", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        
        self.log_textbox = ctk.CTkTextbox(log_frame, font=ctk.CTkFont(family="Consolas", size=12), state="disabled")
        self.log_textbox.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")

        # 4. Action Button Frame
        action_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        action_frame.grid(row=3, column=0, padx=15, pady=15, sticky="ew")
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_columnconfigure(1, weight=1)

        self.start_btn = ctk.CTkButton(
            action_frame, 
            text="Bắt đầu quét SEO & GSC (Start Audit)", 
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color="#00adb5",
            hover_color="#088990",
            command=self.start_audit
        )
        self.start_btn.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")

        self.report_btn = ctk.CTkButton(
            action_frame, 
            text="Mở Báo Cáo HTML (Open Report)", 
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color="#393e46",
            hover_color="#222831",
            state="disabled",
            command=self.open_report
        )
        self.report_btn.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="ew")

    def browse_json(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file service-account.json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if file_path:
            self.json_var.set(file_path)

    def update_max_pages_label(self, value):
        val = int(value)
        self.max_pages_var.set(val)
        self.max_pages_label.configure(text=f"{val} trang")

    def update_threads_label(self, value):
        val = int(value)
        self.threads_var.set(val)
        self.threads_label.configure(text=f"{val} luồng")

    def open_report(self):
        report_path = os.path.abspath(config.REPORT_FILE)
        if os.path.exists(report_path):
            webbrowser.open(f"file:///{report_path}")
        else:
            messagebox.showerror("Lỗi", f"Không tìm thấy file báo cáo tại: {report_path}")

    def update_log_from_queue(self):
        """Đọc log từ queue và đẩy lên CTkTextbox định kỳ."""
        while not self.log_queue.empty():
            try:
                string = self.log_queue.get_nowait()
                self.log_textbox.configure(state="normal")
                self.log_textbox.insert("end", string)
                self.log_textbox.see("end")
                self.log_textbox.configure(state="disabled")
            except queue.Empty:
                break
        
        # Lặp lại sau mỗi 100ms
        self.after(100, self.update_log_from_queue)

    def start_audit(self):
        if self.is_running:
            return

        url = self.url_var.get().strip()
        if not url.startswith(("http://", "https://")):
            messagebox.showerror("Lỗi Cấu Hình", "Website URL phải bắt đầu bằng http:// hoặc https://")
            return

        # Khóa giao diện trong lúc chạy
        self.is_running = True
        self.start_btn.configure(state="disabled", text="Đang quét dữ liệu...")
        self.report_btn.configure(state="disabled")
        self.url_entry.configure(state="disabled")
        self.json_entry.configure(state="disabled")
        self.browse_btn.configure(state="disabled")
        self.max_pages_slider.configure(state="disabled")
        self.thread_slider.configure(state="disabled")

        # Xóa log cũ
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")

        # Khởi chạy luồng quét để tránh block GUI
        audit_thread = threading.Thread(target=self.run_audit_thread, args=(url,))
        audit_thread.daemon = True
        audit_thread.start()

    def run_audit_thread(self, url):
        try:
            # Ghi nhận thời gian bắt đầu
            start_time = time.time()
            
            print("=" * 60)
            print("      SEO CRAWLER & GOOGLE SEARCH CONSOLE AUDIT TOOL      ")
            print("=" * 60)
            print(f"Website mục tiêu: {url}")
            print(f"Cấu hình tối đa: {self.max_pages_var.get()} trang")
            print(f"Số luồng quét: {self.threads_var.get()} luồng")
            print(f"File Credentials: {self.json_var.get()}")
            print("=" * 60 + "\n")

            # 1. Chạy Crawler
            print("[1/3] Đang khởi chạy Bộ quét dữ liệu đa luồng (Crawler)...")
            crawler = SEOCrawler(
                base_url=url,
                max_pages=self.max_pages_var.get(),
                max_workers=self.threads_var.get()
            )
            crawl_results = crawler.run()
            crawl_duration = time.time() - start_time
            print(f"-> Quá trình quét hoàn tất trong {crawl_duration:.1f} giây.\n")

            # 2. Truy xuất Search Console API
            print("[2/3] Đang kết nối tới Google Search Console API...")
            gsc_client = GSCClient(
                credentials_file=self.json_var.get(),
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
            print("\n" + "=" * 60)
            print("                    HOÀN TẤT TIẾN TRÌNH QUÉT               ")
            print("=" * 60)
            print(f"Tổng thời gian xử lý: {total_duration:.1f} giây.")
            print(f"Báo cáo xuất tại: {os.path.abspath(config.REPORT_FILE)}")
            print("=" * 60 + "\n")
            
            # Kích hoạt lại giao diện khi thành công
            self.after(0, lambda: self.audit_finished(success=True))

        except Exception as e:
            print(f"\n[LỖI HỆ THỐNG] Đã xảy ra lỗi trong quá trình quét: {str(e)}")
            import traceback
            traceback.print_exc()
            self.after(0, lambda: self.audit_finished(success=False, error_msg=str(e)))

    def audit_finished(self, success, error_msg=None):
        self.is_running = False
        self.start_btn.configure(state="normal", text="Bắt đầu quét SEO & GSC (Start Audit)")
        self.url_entry.configure(state="normal")
        self.json_entry.configure(state="normal")
        self.browse_btn.configure(state="normal")
        self.max_pages_slider.configure(state="normal")
        self.thread_slider.configure(state="normal")

        if success:
            self.report_btn.configure(state="normal")
            messagebox.showinfo("Thành Công", f"Đã quét xong và xuất báo cáo tại:\n{os.path.abspath(config.REPORT_FILE)}")
            # Tự động mở báo cáo
            self.open_report()
        else:
            messagebox.showerror("Thất Bại", f"Quá trình quét gặp lỗi:\n{error_msg}")

    def __del__(self):
        # Trả lại stdout & stderr nguyên bản khi tắt app
        try:
            sys.stdout = self.original_stdout
            sys.stderr = self.original_stderr
        except AttributeError:
            pass

if __name__ == "__main__":
    # Sửa lỗi hiển thị phông chữ trên Windows High DPI
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = SEOAuditorApp()
    app.mainloop()
