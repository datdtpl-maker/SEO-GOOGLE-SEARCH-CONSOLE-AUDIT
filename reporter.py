import os
import json
from datetime import datetime

class HTMLReporter:
    def __init__(self, report_file, site_url):
        self.report_file = report_file
        self.site_url = site_url

    def generate(self, crawl_data, gsc_data=None):
        visited_pages = crawl_data.get("visited_pages", {})
        broken_links = crawl_data.get("broken_links", [])
        
        # Thống kê On-page
        total_pages = len(visited_pages)
        total_broken = len(broken_links)
        missing_titles = sum(1 for p in visited_pages.values() if p.get("title") == "[Thiếu thẻ Title]")
        missing_desc = sum(1 for p in visited_pages.values() if p.get("meta_desc") == "[Thiếu thẻ Meta Description]")
        multiple_h1 = sum(1 for p in visited_pages.values() if p.get("h1_count", 0) > 1)
        missing_h1 = sum(1 for p in visited_pages.values() if p.get("h1_count", 0) == 0)
        missing_alts = sum(p.get("missing_alts", 0) for p in visited_pages.values())

        # GSC Data
        has_gsc = gsc_data is not None
        gsc_pages = gsc_data.get("pages", {}) if has_gsc else {}
        gsc_queries = gsc_data.get("queries", []) if has_gsc else []
        gsc_sitemaps = gsc_data.get("sitemaps", []) if has_gsc else []

        total_clicks = sum(p.get("clicks", 0) for p in gsc_pages.values()) if has_gsc else 0
        total_impressions = sum(p.get("impressions", 0) for p in gsc_pages.values()) if has_gsc else 0
        avg_ctr = round(sum(p.get("ctr", 0) for p in gsc_pages.values()) / max(len(gsc_pages), 1), 2) if has_gsc else 0

        # HTML Template
        html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Audit & Search Console Dashboard - {self.site_url}</title>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <!-- FontAwesome for icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Chart.js for data visualization -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <style>
        :root {{
            --bg-primary: #0b0f19;
            --bg-secondary: #161c2d;
            --bg-glass: rgba(22, 28, 45, 0.7);
            --border-glass: rgba(255, 255, 255, 0.08);
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --accent-blue: #3b82f6;
            --accent-purple: #8b5cf6;
            --accent-emerald: #10b981;
            --accent-rose: #f43f5e;
            --accent-amber: #f59e0b;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }}

        body {{
            background-color: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 24px;
            background-image: 
                radial-gradient(at 10% 10%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
                radial-gradient(at 90% 90%, rgba(139, 92, 246, 0.15) 0px, transparent 50%);
            background-attachment: fixed;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        /* Header */
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            background: var(--bg-glass);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-glass);
            border-radius: 16px;
            margin-bottom: 24px;
        }}

        .logo-section h1 {{
            font-size: 24px;
            font-weight: 800;
            background: linear-gradient(135deg, #60a5fa, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .logo-section p {{
            font-size: 13px;
            color: var(--text-secondary);
            margin-top: 4px;
        }}

        .time-badge {{
            background: rgba(255, 255, 255, 0.05);
            padding: 8px 16px;
            border-radius: 99px;
            border: 1px solid var(--border-glass);
            font-size: 13px;
            color: var(--text-secondary);
        }}

        /* GSC Warning Banner */
        .gsc-banner-warning {{
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(244, 63, 94, 0.15));
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 16px;
        }}

        .gsc-banner-warning i {{
            font-size: 24px;
            color: var(--accent-amber);
        }}

        .gsc-banner-warning div h4 {{
            font-size: 15px;
            color: var(--text-primary);
        }}

        .gsc-banner-warning div p {{
            font-size: 13px;
            color: var(--text-secondary);
            margin-top: 4px;
        }}

        /* Grid Stats */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }}

        .stat-card {{
            background: var(--bg-glass);
            backdrop-filter: blur(8px);
            border: 1px solid var(--border-glass);
            border-radius: 16px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            transition: transform 0.2s, border-color 0.2s;
        }}

        .stat-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.15);
        }}

        .stat-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--text-secondary);
            font-size: 13px;
            font-weight: 500;
        }}

        .stat-icon {{
            width: 36px;
            height: 36px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
        }}

        .stat-icon.blue {{ background: rgba(59, 130, 246, 0.1); color: var(--accent-blue); }}
        .stat-icon.rose {{ background: rgba(244, 63, 94, 0.1); color: var(--accent-rose); }}
        .stat-icon.amber {{ background: rgba(245, 158, 11, 0.1); color: var(--accent-amber); }}
        .stat-icon.emerald {{ background: rgba(16, 185, 129, 0.1); color: var(--accent-emerald); }}
        .stat-icon.purple {{ background: rgba(139, 92, 246, 0.1); color: var(--accent-purple); }}

        .stat-val {{
            font-size: 28px;
            font-weight: 800;
            margin-top: 12px;
            color: var(--text-primary);
        }}

        /* Main Content with Tabs */
        .content-section {{
            background: var(--bg-glass);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-glass);
            border-radius: 20px;
            padding: 24px;
            margin-bottom: 24px;
        }}

        .tabs {{
            display: flex;
            gap: 8px;
            border-bottom: 1px solid var(--border-glass);
            padding-bottom: 12px;
            margin-bottom: 24px;
            overflow-x: auto;
        }}

        .tab-btn {{
            background: transparent;
            border: none;
            color: var(--text-secondary);
            padding: 10px 20px;
            font-size: 14px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s;
            white-space: nowrap;
        }}

        .tab-btn:hover {{
            background: rgba(255, 255, 255, 0.03);
            color: var(--text-primary);
        }}

        .tab-btn.active {{
            background: rgba(59, 130, 246, 0.1);
            color: var(--accent-blue);
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        /* Table & Lists */
        .table-controls {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            gap: 16px;
            flex-wrap: wrap;
        }}

        .search-box {{
            position: relative;
            flex: 1;
            max-width: 400px;
        }}

        .search-box i {{
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-secondary);
            font-size: 14px;
        }}

        .search-input {{
            width: 100%;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-glass);
            padding: 10px 16px 10px 40px;
            border-radius: 10px;
            color: var(--text-primary);
            font-size: 14px;
            transition: border-color 0.2s;
        }}

        .search-input:focus {{
            border-color: var(--accent-blue);
            outline: none;
        }}

        .filter-select {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-glass);
            padding: 10px 16px;
            border-radius: 10px;
            color: var(--text-primary);
            font-size: 14px;
            outline: none;
            cursor: pointer;
        }}

        .table-wrapper {{
            width: 100%;
            overflow-x: auto;
            border-radius: 12px;
            border: 1px solid var(--border-glass);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 14px;
        }}

        th {{
            background: rgba(255, 255, 255, 0.02);
            color: var(--text-secondary);
            font-weight: 600;
            padding: 14px 16px;
            border-bottom: 1px solid var(--border-glass);
        }}

        td {{
            padding: 14px 16px;
            border-bottom: 1px solid var(--border-glass);
            color: var(--text-primary);
            max-width: 400px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        tr:hover td {{
            background: rgba(255, 255, 255, 0.01);
        }}

        .link-text {{
            color: var(--accent-blue);
            text-decoration: none;
        }}

        .link-text:hover {{
            text-decoration: underline;
        }}

        /* Status Badge */
        .badge {{
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            display: inline-block;
        }}

        .badge.danger {{ background: rgba(244, 63, 94, 0.15); color: var(--accent-rose); }}
        .badge.warning {{ background: rgba(245, 158, 11, 0.15); color: var(--accent-amber); }}
        .badge.success {{ background: rgba(16, 185, 129, 0.15); color: var(--accent-emerald); }}
        .badge.secondary {{ background: rgba(255, 255, 255, 0.05); color: var(--text-secondary); }}

        /* Charts Layout */
        .charts-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }}

        .chart-box {{
            background: var(--bg-glass);
            border: 1px solid var(--border-glass);
            border-radius: 16px;
            padding: 20px;
        }}

        .chart-box h3 {{
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 20px;
            color: var(--text-primary);
        }}

        .chart-container {{
            position: relative;
            height: 300px;
            width: 100%;
        }}

        /* GSC Config Guide */
        .guide-section {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-glass);
            border-radius: 12px;
            padding: 20px;
            margin-top: 16px;
        }}

        .guide-section h4 {{
            font-size: 15px;
            margin-bottom: 12px;
            color: var(--text-primary);
        }}

        .guide-section ol {{
            padding-left: 20px;
            font-size: 13.5px;
            line-height: 1.8;
            color: var(--text-secondary);
        }}

        .guide-code {{
            background: #000;
            color: #10b981;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }}

        .code-block {{
            background: #000;
            padding: 12px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 13px;
            margin: 10px 0;
            overflow-x: auto;
            color: #f3f4f6;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}

    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header>
            <div class="logo-section">
                <h1>SEO & GOOGLE SEARCH CONSOLE AUDIT</h1>
                <p>Địa chỉ web: <a href="{self.site_url}" class="link-text" target="_blank">{self.site_url}</a></p>
            </div>
            <div class="time-badge">
                <i class="fa-regular fa-clock"></i> Báo cáo xuất lúc: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
            </div>
        </header>

        <!-- GSC Warning Banner (Nếu chưa kết nối GSC) -->
        {"" if has_gsc else f"""
        <div class="gsc-banner-warning">
            <i class="fa-solid fa-triangle-exclamation"></i>
            <div>
                <h4>Chưa kết nối API Google Search Console</h4>
                <p>Công cụ đang chạy ở chế độ <b>Quét Ngoại Tuyến (Offline Crawler)</b>. Hãy đọc tab "Hướng dẫn kết nối" bên dưới để liên kết dữ liệu GSC.</p>
            </div>
        </div>
        """}

        <!-- Stats Grid -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-header">
                    <span>ĐÃ QUÉT THỰC TẾ</span>
                    <div class="stat-icon blue"><i class="fa-solid fa-spider"></i></div>
                </div>
                <div class="stat-val">{total_pages} trang</div>
            </div>
            <div class="stat-card">
                <div class="stat-header">
                    <span>LIÊN KẾT HỎNG (404)</span>
                    <div class="stat-icon rose"><i class="fa-solid fa-link-slash"></i></div>
                </div>
                <div class="stat-val" style="color: { 'var(--accent-rose)' if total_broken > 0 else 'var(--text-primary)' }">{total_broken} liên kết</div>
            </div>
            <div class="stat-card">
                <div class="stat-header">
                    <span>LƯỢT CLICK (GSC - 30 ngày)</span>
                    <div class="stat-icon emerald"><i class="fa-solid fa-mouse-pointer"></i></div>
                </div>
                <div class="stat-val">{f"{total_clicks:,}" if has_gsc else "N/A"}</div>
            </div>
            <div class="stat-card">
                <div class="stat-header">
                    <span>LƯỢT HIỂN THỊ (GSC - 30 ngày)</span>
                    <div class="stat-icon purple"><i class="fa-solid fa-eye"></i></div>
                </div>
                <div class="stat-val">{f"{total_impressions:,}" if has_gsc else "N/A"}</div>
            </div>
            <div class="stat-card">
                <div class="stat-header">
                    <span>CTR TRUNG BÌNH (GSC)</span>
                    <div class="stat-icon amber"><i class="fa-solid fa-chart-line"></i></div>
                </div>
                <div class="stat-val">{avg_ctr}%</div>
            </div>
        </div>

        <!-- Main Audit Content -->
        <div class="content-section">
            <div class="tabs">
                <button class="tab-btn active" onclick="switchTab('tab-broken')"><i class="fa-solid fa-circle-exclamation"></i> Liên kết hỏng ({total_broken})</button>
                <button class="tab-btn" onclick="switchTab('tab-onpage')"><i class="fa-solid fa-file-invoice"></i> Tối ưu On-page ({total_pages})</button>
                {f'<button class="tab-btn" onclick="switchTab(&quot;tab-gsc-pages&quot;)"><i class="fa-solid fa-globe"></i> Trang Hiệu Suất ({len(gsc_pages)})</button>' if has_gsc else ''}
                {f'<button class="tab-btn" onclick="switchTab(&quot;tab-gsc-queries&quot;)"><i class="fa-solid fa-magnifying-glass"></i> Từ khóa hàng đầu ({len(gsc_queries)})</button>' if has_gsc else ''}
                {f'<button class="tab-btn" onclick="switchTab(&quot;tab-sitemaps&quot;)"><i class="fa-solid fa-sitemap"></i> Sitemaps ({len(gsc_sitemaps)})</button>' if has_gsc else ''}
                <button class="tab-btn" onclick="switchTab('tab-guide')"><i class="fa-solid fa-circle-info"></i> Hướng dẫn kết nối</button>
            </div>

            <!-- Tab 1: Broken Links -->
            <div id="tab-broken" class="tab-content active">
                <div class="table-controls">
                    <h3>Danh sách các liên kết bị hỏng (404/Lỗi kết nối)</h3>
                    <div class="search-box">
                        <i class="fa-solid fa-magnifying-glass"></i>
                        <input type="text" class="search-input" id="search-broken" placeholder="Tìm kiếm liên kết..." onkeyup="filterTable('table-broken', 'search-broken')">
                    </div>
                </div>
                
                <div class="table-wrapper">
                    <table id="table-broken">
                        <thead>
                            <tr>
                                <th>URL bị lỗi</th>
                                <th>Mã lỗi</th>
                                <th>Mô tả lỗi</th>
                                <th>Tìm thấy trên trang (Nguồn)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"<tr><td colspan='4' style='text-align:center;color:var(--accent-emerald);padding:30px;'><i class='fa-solid fa-circle-check' style='font-size:24px;margin-bottom:10px;display:block;'></i>Tuyệt vời! Không tìm thấy liên kết hỏng nào trên website của bạn.</td></tr>" if total_broken == 0 else ""}
                            {"".join([f"""
                            <tr>
                                <td><a href='{link.get("url")}' class='link-text' target='_blank'>{link.get("url")}</a></td>
                                <td><span class='badge danger'>{link.get("status_code")}</span></td>
                                <td>{link.get("error", "Không tìm thấy")}</td>
                                <td><a href='{link.get("parent") or "#"}' class='link-text' target='_blank'>{link.get("parent") or "Không xác định"}</a></td>
                            </tr>
                            """ for link in broken_links])}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Tab 2: Onpage SEO -->
            <div id="tab-onpage" class="tab-content">
                <div class="table-controls">
                    <h3>Phân tích tối ưu hóa On-page SEO cho các trang đã quét</h3>
                    <div style="display:flex; gap:12px;">
                        <select class="filter-select" id="filter-onpage" onchange="filterOnpage()">
                            <option value="all">Tất cả trang</option>
                            <option value="missing-desc">Thiếu Mô tả (Meta Description)</option>
                            <option value="h1-error">Lỗi thẻ H1 (>1 hoặc 0)</option>
                            <option value="missing-alt">Có ảnh thiếu thẻ Alt</option>
                        </select>
                        <div class="search-box">
                            <i class="fa-solid fa-magnifying-glass"></i>
                            <input type="text" class="search-input" id="search-onpage" placeholder="Tìm tên trang hoặc URL..." onkeyup="filterTable('table-onpage', 'search-onpage')">
                        </div>
                    </div>
                </div>

                <div class="table-wrapper">
                    <table id="table-onpage">
                        <thead>
                            <tr>
                                <th>Địa chỉ trang (URL)</th>
                                <th>Tiêu đề (Title)</th>
                                <th>Mô tả (Meta Description)</th>
                                <th>Thẻ H1</th>
                                <th>Ảnh thiếu Alt</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join([f"""
                            <tr data-desc='{"missing" if p.get("meta_desc") == "[Thiếu thẻ Meta Description]" else "ok"}' data-h1='{"error" if p.get("h1_count", 0) != 1 else "ok"}' data-alt='{"error" if p.get("missing_alts", 0) > 0 else "ok"}'>
                                <td><a href='{url}' class='link-text' target='_blank'>{url}</a></td>
                                <td>{p.get("title")}</td>
                                <td>
                                    <span class='{ "badge danger" if p.get("meta_desc") == "[Thiếu thẻ Meta Description]" else "" }'>
                                        {p.get("meta_desc")}
                                    </span>
                                </td>
                                <td>
                                    <span class='badge { "danger" if p.get("h1_count") != 1 else "success" }'>
                                        {p.get("h1_count")} thẻ H1
                                    </span>
                                </td>
                                <td>
                                    <span class='badge { "warning" if p.get("missing_alts", 0) > 0 else "success" }'>
                                        {p.get("missing_alts")} ảnh
                                    </span>
                                </td>
                            </tr>
                            """ for url, p in visited_pages.items() if p != {"status": "processing"}])}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Tab 3: GSC Pages -->
            {f"""
            <div id="tab-gsc-pages" class="tab-content">
                <div class="table-controls">
                    <h3>Hiệu suất hiển thị và lượt click của các trang trên Google Search Console</h3>
                    <div class="search-box">
                        <i class="fa-solid fa-magnifying-glass"></i>
                        <input type="text" class="search-input" id="search-gsc-pages" placeholder="Tìm kiếm trang..." onkeyup="filterTable('table-gsc-pages', 'search-gsc-pages')">
                    </div>
                </div>

                <div class="table-wrapper">
                    <table id="table-gsc-pages">
                        <thead>
                            <tr>
                                <th>Địa chỉ trang (URL)</th>
                                <th>Lượt Click</th>
                                <th>Lượt Hiển thị</th>
                                <th>Tỷ lệ Click (CTR)</th>
                                <th>Vị trí trung bình</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join([f"""
                            <tr>
                                <td><a href='{url}' class='link-text' target='_blank'>{url}</a></td>
                                <td style='font-weight:700;'>{info.get("clicks"):,}</td>
                                <td>{info.get("impressions"):,}</td>
                                <td>{info.get("ctr")}%</td>
                                <td>{info.get("position")}</td>
                            </tr>
                            """ for url, info in gsc_pages.items()])}
                        </tbody>
                    </table>
                </div>
            </div>
            """ if has_gsc else ""}

            <!-- Tab 4: GSC Queries -->
            {f"""
            <div id="tab-gsc-queries" class="tab-content">
                <div class="table-controls">
                    <h3>Top 100 từ khóa mang lại lượng truy cập nhiều nhất cho website</h3>
                    <div class="search-box">
                        <i class="fa-solid fa-magnifying-glass"></i>
                        <input type="text" class="search-input" id="search-gsc-queries" placeholder="Tìm kiếm từ khóa..." onkeyup="filterTable('table-gsc-queries', 'search-gsc-queries')">
                    </div>
                </div>

                <div class="table-wrapper">
                    <table id="table-gsc-queries">
                        <thead>
                            <tr>
                                <th>Cụm từ tìm kiếm (Từ khóa)</th>
                                <th>Lượt Click</th>
                                <th>Lượt Hiển thị</th>
                                <th>Tỷ lệ Click (CTR)</th>
                                <th>Vị trí trung bình</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join([f"""
                            <tr>
                                <td style='font-weight:600;color:var(--text-primary);'>{item.get("query")}</td>
                                <td style='font-weight:700;color:var(--accent-emerald);'>{item.get("clicks"):,}</td>
                                <td>{item.get("impressions"):,}</td>
                                <td>{item.get("ctr")}%</td>
                                <td>{item.get("position")}</td>
                            </tr>
                            """ for item in gsc_queries])}
                        </tbody>
                    </table>
                </div>
            </div>
            """ if has_gsc else ""}

            <!-- Tab 5: Sitemaps -->
            {f"""
            <div id="tab-sitemaps" class="tab-content">
                <div class="table-controls">
                    <h3>Trạng thái các sơ đồ trang web (Sitemaps) đã gửi cho Google</h3>
                </div>

                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>Đường dẫn Sitemap</th>
                                <th>Lần gửi cuối cùng</th>
                                <th>Lần Google tải cuối cùng</th>
                                <th>Cảnh báo</th>
                                <th>Lỗi</th>
                                <th>Trạng thái</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join([f"""
                            <tr>
                                <td><a href='{item.get("path")}' class='link-text' target='_blank'>{item.get("path")}</a></td>
                                <td>{item.get("last_submitted")}</td>
                                <td>{item.get("last_downloaded")}</td>
                                <td>{item.get("warnings")}</td>
                                <td style='color:{"var(--accent-rose)" if item.get("errors", 0) > 0 else "var(--text-primary)"}'>{item.get("errors")}</td>
                                <td>
                                    <span class='badge {"success" if item.get("errors", 0) == 0 else "danger"}'>
                                        {"Hoạt động tốt" if item.get("errors", 0) == 0 else "Có lỗi"}
                                    </span>
                                </td>
                            </tr>
                            """ for item in gsc_sitemaps])}
                        </tbody>
                    </table>
                </div>
            </div>
            """ if has_gsc else ""}

            <!-- Tab 6: Guide -->
            <div id="tab-guide" class="tab-content">
                <h3>Hướng dẫn thiết lập Google Search Console API</h3>
                <div class="guide-section">
                    <h4>Bước 1: Tạo tài khoản Service Account</h4>
                    <ol>
                        <li>Vào trang <a href="https://console.cloud.google.com/" target="_blank" class="link-text">Google Cloud Console</a>.</li>
                        <li>Tạo một dự án Google Cloud mới.</li>
                        <li>Tìm thanh tìm kiếm tìm từ khóa <b>"Google Search Console API"</b> và nhấp <b>Enable (Kích hoạt)</b>.</li>
                        <li>Vào menu bên trái chọn <b>IAM & Admin > Service Accounts</b>.</li>
                        <li>Nhấp <b>Create Service Account</b> (Tạo tài khoản dịch vụ), điền thông tin và bấm Create.</li>
                        <li>Nhấp vào tài khoản vừa tạo, chọn tab <b>Keys</b> -> <b>Add Key</b> -> <b>Create new key</b> -> Chọn định dạng <b>JSON</b>.</li>
                        <li>Tải xuống file key JSON, đổi tên nó thành <span class="guide-code">service-account.json</span> và sao chép bỏ vào thư mục chứa code dự án này.</li>
                    </ol>
                </div>
                
                <div class="guide-section" style="margin-top: 20px;">
                    <h4>Bước 2: Phân quyền trong Google Search Console</h4>
                    <ol>
                        <li>Mở file JSON key vừa tải, tìm và copy địa chỉ email tài khoản dịch vụ (có dạng: <span class="guide-code">xxx@xxx.iam.gserviceaccount.com</span>).</li>
                        <li>Truy cập <a href="https://search.google.com/search-console" target="_blank" class="link-text">Google Search Console</a> của bạn.</li>
                        <li>Vào mục <b>Cài đặt (Settings) > Người dùng và quyền (Users & permissions)</b>.</li>
                        <li>Nhấp **Thêm người dùng (Add user)**.</li>
                        <li>Dán địa chỉ email vừa copy vào, chọn quyền **Người xem (Viewer)** và lưu lại.</li>
                    </ol>
                </div>
            </div>
        </div>
    </div>

    <script>
        function switchTab(tabId) {{
            // Ẩn tất cả tab nội dung
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(c => c.classList.remove('active'));

            // Hủy kích hoạt tất cả nút bấm tab
            const buttons = document.querySelectorAll('.tab-btn');
            buttons.forEach(b => b.classList.remove('active'));

            // Hiển thị tab được chọn
            document.getElementById(tabId).classList.add('active');
            
            // Kích hoạt nút bấm tương ứng
            event.currentTarget.classList.add('active');
        }}

        function filterTable(tableId, inputId) {{
            const input = document.getElementById(inputId);
            const filter = input.value.toLowerCase();
            const table = document.getElementById(tableId);
            const trs = table.getElementsByTagName('tr');

            for (let i = 1; i < trs.length; i++) {{
                let match = false;
                const tds = trs[i].getElementsByTagName('td');
                for (let j = 0; j < tds.length; j++) {{
                    if (tds[j]) {{
                        const text = tds[j].textContent || tds[j].innerText;
                        if (text.toLowerCase().indexOf(filter) > -1) {{
                            match = true;
                            break;
                        }}
                    }}
                }}
                trs[i].style.display = match ? '' : 'none';
            }}
        }}

        function filterOnpage() {{
            const select = document.getElementById('filter-onpage');
            const type = select.value;
            const table = document.getElementById('table-onpage');
            const trs = table.getElementsByTagName('tr');

            for (let i = 1; i < trs.length; i++) {{
                const tr = trs[i];
                if (type === 'all') {{
                    tr.style.display = '';
                }} else if (type === 'missing-desc') {{
                    tr.style.display = tr.getAttribute('data-desc') === 'missing' ? '' : 'none';
                }} else if (type === 'h1-error') {{
                    tr.style.display = tr.getAttribute('data-h1') === 'error' ? '' : 'none';
                }} else if (type === 'missing-alt') {{
                    tr.style.display = tr.getAttribute('data-alt') === 'error' ? '' : 'none';
                }}
            }}
        }}
    </script>
</body>
</html>
"""
        with open(self.report_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"[Thành công] Báo cáo SEO đã được xuất ra file: {os.path.abspath(self.report_file)}")
