import os
import sys
from reporter import HTMLReporter

# Cấu hình mã hóa UTF-8 cho Windows console
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def main():
    print("=" * 60)

    print("      MÔ PHỎNG DỮ LIỆU ĐỂ KIỂM TRA GIAO DIỆN BÁO CÁO       ")
    print("=" * 60)
    
    site_url = "https://khaihoanderma.com/"
    report_file = "seo_audit_report_sample.html"

    # Dữ liệu quét giả lập
    mock_crawl = {
        "visited_pages": {
            "https://khaihoanderma.com/": {
                "title": "Khải Hoàn Derma - Dược mỹ phẩm chính hãng & Chăm sóc da y khoa",
                "meta_desc": "Nhà thuốc Khải Hoàn chuyên cung cấp các sản phẩm chăm sóc da chuẩn y khoa, sữa rửa mặt, kem chống nắng, serum trị mụn chính hãng từ La Roche-Posay, Obagi, Cerave.",
                "h1_count": 1,
                "missing_alts": 2,
                "parent": None
            },
            "https://khaihoanderma.com/danh-muc/cham-soc-da/": {
                "title": "Sản phẩm Chăm Sóc Da Chuẩn Y Khoa | Khải Hoàn Derma",
                "meta_desc": "Danh mục sản phẩm chăm sóc da chính hãng: kem dưỡng ẩm, tẩy trang, toner.",
                "h1_count": 1,
                "missing_alts": 0,
                "parent": "https://khaihoanderma.com/"
            },
            "https://khaihoanderma.com/product/kem-tri-mun-obagi-tretinoin-0-05/": {
                "title": "Kem Trị Mụn Obagi Tretinoin 0.05% Cream Chính Hãng",
                "meta_desc": "[Thiếu thẻ Meta Description]",
                "h1_count": 2,
                "missing_alts": 1,
                "parent": "https://khaihoanderma.com/danh-muc/cham-soc-da/"
            },
            "https://khaihoanderma.com/lien-he/": {
                "title": "[Thiếu thẻ Title]",
                "meta_desc": "Liên hệ với nhà thuốc Khải Hoàn tại Phan Thiết, Bình Thuận.",
                "h1_count": 0,
                "missing_alts": 0,
                "parent": "https://khaihoanderma.com/"
            }
        },
        "broken_links": [
            {
                "url": "https://khaihoanderma.com/items/F135991237",
                "status_code": 410,
                "error": "HTTP 410 Gone (Được chặn bởi robots.txt)",
                "parent": "https://khaihoanderma.com/product/kem-tri-mun-obagi-tretinoin-0-05/"
            },
            {
                "url": "https://khaihoanderma.com/items?112842957",
                "status_code": 410,
                "error": "HTTP 410 Gone",
                "parent": "https://khaihoanderma.com/"
            },
            {
                "url": "https://khaihoanderma.com/gio-hang/?remove_item=ff7df525b3be596a51fb9",
                "status_code": 404,
                "error": "HTTP 404 Not Found (Link hệ thống giỏ hàng rác)",
                "parent": "https://khaihoanderma.com/danh-muc/cham-soc-da/"
            }
        ]
    }

    # Dữ liệu Google Search Console giả lập
    mock_gsc = {
        "pages": {
            "https://khaihoanderma.com/": {
                "clicks": 1420,
                "impressions": 25400,
                "ctr": 5.59,
                "position": 4.2
            },
            "https://khaihoanderma.com/product/kem-tri-mun-obagi-tretinoin-0-05/": {
                "clicks": 450,
                "impressions": 8600,
                "ctr": 5.23,
                "position": 8.7
            },
            "https://khaihoanderma.com/danh-muc/cham-soc-da/": {
                "clicks": 280,
                "impressions": 12000,
                "ctr": 2.33,
                "position": 12.1
            }
        },
        "queries": [
            {"query": "khải hoàn derma", "clicks": 820, "impressions": 2100, "ctr": 39.05, "position": 1.0},
            {"query": "tretinoin obagi 0.05", "clicks": 210, "impressions": 3400, "ctr": 6.18, "position": 4.5},
            {"query": "kem trị mụn obagi", "clicks": 150, "impressions": 2800, "ctr": 5.36, "position": 6.2},
            {"query": "dược mỹ phẩm phan thiết", "clicks": 95, "impressions": 1200, "ctr": 7.92, "position": 2.1}
        ],
        "sitemaps": [
            {
                "path": "https://khaihoanderma.com/sitemap.xml",
                "last_submitted": "2026-06-12T05:00:00Z",
                "last_downloaded": "2026-06-15T12:00:00Z",
                "warnings": 0,
                "errors": 0
            }
        ]
    }

    reporter = HTMLReporter(report_file, site_url)
    reporter.generate(mock_crawl, mock_gsc)

    print("\n" + "=" * 60)
    print("                 ĐÃ TẠO FILE BÁO CÁO MẪU THÀNH CÔNG             ")
    print("=" * 60)
    print(f"Báo cáo mẫu của bạn tại: {os.path.abspath(report_file)}")
    print("Hãy nhấp đúp vào file trên để trải nghiệm thử giao diện Dashboard.")
    print("=" * 60)

if __name__ == "__main__":
    main()
