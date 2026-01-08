"""
Unit tests for HTML Converter
測試 JSON 轉 HTML 的核心功能
使用 pytest 框架
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from managers.html_converter import TrendReportHTMLConverter
from managers.html_themes import THEMES, CATEGORY_CONFIG


@pytest.fixture
def sample_data():
    """測試資料 fixture"""
    return {
        "趨勢報告": "這是一個測試趨勢報告，包含多個重要趨勢分析。",
        "關鍵字": ["AI", "機器學習", "自動化", "數位轉型"],
        "主要趨勢1": {
            "標題": "人工智慧技術突破",
            "<a>趨勢洞察": "AI 技術在各領域快速發展，特別是生成式 AI。",
            "<b>Hashtag關鍵詞": ["GenerativeAI", "ChatGPT", "LLM"],
            "<c>代表事件": [
                {
                    "事件": "OpenAI 發布 GPT-4",
                    "分析": "大型語言模型性能大幅提升",
                    "來源": "TechCrunch",
                    "關聯度": "高度相關"
                }
            ],
            "<d>重要關係人": {
                "供給端": "科技公司、研究機構",
                "需求端": "企業用戶、一般消費者",
                "代表性意義": "AI 民主化進程加速"
            },
            "<e>缺口": [
                "AI 倫理規範尚未完善",
                "資料隱私保護需求增加"
            ],
            "<f>未來產品或服務機會點": [
                "企業級 AI 顧問服務",
                "個人化 AI 助理"
            ],
            "<g>關鍵驅動因素": {
                "a社會": "數位轉型需求",
                "b政治": "AI 監管政策",
                "c經濟": "降低成本壓力",
                "d文化": "接受新科技態度"
            },
            "<h>微弱信號": [
                "開源 AI 模型興起",
                "邊緣運算 AI 發展"
            ],
            "<i>時間尺度": "短期（1-2年）",
            "<j>趨勢總結洞察": "AI 技術將持續快速發展並深入各行各業。"
        }
    }


@pytest.fixture
def category():
    """類別 fixture"""
    return "technological"


@pytest.fixture
def date_range():
    """日期範圍 fixture"""
    return "2025-10-01-2025-10-31"


class TestTrendReportHTMLConverter:
    """測試 TrendReportHTMLConverter 類別"""
    
    def test_initialization(self, sample_data, category, date_range):
        """測試轉換器初始化"""
        converter = TrendReportHTMLConverter(
            data=sample_data,
            category=category,
            date_range=date_range
        )
        
        assert converter.category == category
        assert converter.date_range == date_range
        assert converter.data == sample_data
        assert converter.config is not None
    
    def test_get_default_theme(self, sample_data, date_range):
        """測試取得預設主題"""
        converter = TrendReportHTMLConverter(
            data=sample_data,
            category="technological",
            date_range=date_range
        )
        
        theme = converter.get_theme()
        assert theme == "blue-purple-gradient"
    
    def test_get_custom_theme(self, sample_data, category, date_range):
        """測試使用自訂主題"""
        converter = TrendReportHTMLConverter(
            data=sample_data,
            category=category,
            date_range=date_range,
            custom_theme="sunset"
        )
        
        theme = converter.get_theme()
        assert theme == "sunset"
    
    def test_get_theme_colors(self, sample_data, category, date_range):
        """測試取得主題顏色"""
        converter = TrendReportHTMLConverter(
            data=sample_data,
            category=category,
            date_range=date_range
        )
        
        colors = converter.get_theme_colors("blue")
        assert len(colors) == 2
        assert colors[0].startswith('#')
        assert colors[1].startswith('#')
    
    def test_generate_html_structure(self, sample_data, category, date_range):
        """測試生成完整 HTML 結構"""
        converter = TrendReportHTMLConverter(
            data=sample_data,
            category=category,
            date_range=date_range
        )
        
        html = converter.generate_html()
        
        # 檢查基本 HTML 結構
        assert '<!DOCTYPE html>' in html
        assert '<html lang="zh-TW">' in html
        assert '<head>' in html
        assert '<body>' in html
        assert '</html>' in html
        
        # 檢查編碼
        assert 'charset="UTF-8"' in html
        
        # 檢查標題
        assert '人工智慧技術發展趨勢報告' in html
    
    def test_generate_css(self, sample_data, category, date_range):
        """測試生成 CSS"""
        converter = TrendReportHTMLConverter(
            data=sample_data,
            category=category,
            date_range=date_range
        )
        
        colors = converter.get_theme_colors(converter.get_theme())
        css = converter._generate_css(colors)
        
        # 檢查 CSS 包含必要的樣式
        assert '.container' in css
        assert '.header' in css
        assert '.trend-card' in css
        assert 'font-family' in css
        
        # 檢查顏色有套用
        assert colors[0] in css
        assert colors[1] in css
        
        # 檢查響應式設計
        assert '@media' in css
    
    def test_generate_header(self, sample_data, category, date_range):
        """測試生成標題區塊"""
        converter = TrendReportHTMLConverter(
            data=sample_data,
            category=category,
            date_range=date_range
        )
        
        header = converter._generate_header()
        
        assert '<div class="header">' in header
        assert '<h1>' in header
        assert '人工智慧技術發展趨勢報告' in header
        assert '時間區間' in header
    
    def test_generate_summary(self, sample_data, category, date_range):
        """測試生成概述區塊"""
        converter = TrendReportHTMLConverter(
            data=sample_data,
            category=category,
            date_range=date_range
        )
        
        summary = converter._generate_summary()
        
        assert '趨勢概述' in summary
        assert sample_data['趨勢報告'] in summary
        
        # 檢查關鍵字（technological 類別應該顯示關鍵字）
        assert '關鍵字' in summary
        for keyword in sample_data['關鍵字']:
            assert keyword in summary
    
    def test_generate_summary_without_keywords(self, sample_data, date_range):
        """測試不顯示關鍵字的類別"""
        converter = TrendReportHTMLConverter(
            data=sample_data,
            category="business_and_investment",
            date_range=date_range
        )
        
        summary = converter._generate_summary()
        
        # business_and_investment 不應該有關鍵字區塊
        keyword_section_count = summary.count('keywords-section')
        assert keyword_section_count == 0
    
    def test_generate_trend_card(self, sample_data, category, date_range):
        """測試生成趨勢卡片"""
        converter = TrendReportHTMLConverter(
            data=sample_data,
            category=category,
            date_range=date_range
        )
        
        trend = sample_data['主要趨勢1']
        card = converter._generate_trend_card(trend)
        
        # 檢查卡片結構
        assert '<div class="trend-card">' in card
        assert trend['標題'] in card
        
        # 檢查各個區塊
        assert '趨勢洞察' in card
        assert 'Hashtag 關鍵詞' in card
        assert '代表事件' in card
        assert '重要關係人' in card
        assert '議題缺口' in card
        assert '未來產品或服務機會點' in card
        assert '關鍵驅動因素' in card
        assert '微弱信號' in card
        assert '時間尺度' in card
        assert '趨勢總結洞察' in card
    
    def test_generate_trends(self, sample_data, category, date_range):
        """測試生成所有趨勢"""
        # 添加多個趨勢
        data_with_multiple_trends = sample_data.copy()
        data_with_multiple_trends['主要趨勢2'] = {
            "標題": "第二個趨勢",
            "<a>趨勢洞察": "測試第二個趨勢"
        }
        
        converter = TrendReportHTMLConverter(
            data=data_with_multiple_trends,
            category=category,
            date_range=date_range
        )
        
        trends = converter._generate_trends()
        
        # 應該包含兩個趨勢卡片
        card_count = trends.count('<div class="trend-card">')
        assert card_count == 2
    
    @pytest.mark.parametrize("test_category", [
        'business_and_investment',
        'political',
        'technological',
        'economic',
        'environmental',
        'social'
    ])
    def test_all_categories(self, sample_data, date_range, test_category):
        """測試所有類別配置"""
        converter = TrendReportHTMLConverter(
            data=sample_data,
            category=test_category,
            date_range=date_range
        )
        
        html = converter.generate_html()
        
        # 檢查每個類別都能成功生成 HTML
        assert '<!DOCTYPE html>' in html
        assert CATEGORY_CONFIG[test_category]['title'] in html
    
    @pytest.mark.parametrize("theme_name", list(THEMES.keys()))
    def test_all_themes(self, sample_data, category, date_range, theme_name):
        """測試所有主題"""
        converter = TrendReportHTMLConverter(
            data=sample_data,
            category=category,
            date_range=date_range,
            custom_theme=theme_name
        )
        
        html = converter.generate_html()
        colors = THEMES[theme_name]['gradient']
        
        # 檢查主題顏色有套用
        assert colors[0] in html
        assert colors[1] in html
    
    def test_missing_optional_fields(self, category, date_range):
        """測試缺少可選欄位的情況"""
        minimal_data = {
            "趨勢報告": "最小化測試資料",
            "關鍵字": ["測試"],
            "主要趨勢1": {
                "標題": "最小趨勢",
                "<a>趨勢洞察": "只有必要欄位"
            }
        }
        
        converter = TrendReportHTMLConverter(
            data=minimal_data,
            category=category,
            date_range=date_range
        )
        
        # 應該能夠正常生成 HTML，不會拋出異常
        html = converter.generate_html()
        assert '<!DOCTYPE html>' in html
        assert '最小趨勢' in html
    
    def test_event_with_different_source_key(self, sample_data, category, date_range):
        """測試事件有不同的來源欄位名稱"""
        data_with_alt_source = sample_data.copy()
        data_with_alt_source['主要趨勢1']['<c>代表事件'] = [
            {
                "事件": "測試事件",
                "分析": "測試分析",
                "(來源": "替代來源欄位",
                "關聯度": "高"
            }
        ]
        
        converter = TrendReportHTMLConverter(
            data=data_with_alt_source,
            category=category,
            date_range=date_range
        )
        
        card = converter._generate_trend_card(data_with_alt_source['主要趨勢1'])
        
        # 應該能處理替代的來源欄位
        assert '替代來源欄位' in card


class TestHTMLOutput:
    """測試 HTML 輸出品質"""
    
    def test_html_validity(self):
        """測試 HTML 基本有效性"""
        sample_data = {
            "趨勢報告": "測試報告",
            "關鍵字": ["測試"],
            "主要趨勢1": {
                "標題": "測試趨勢",
                "<a>趨勢洞察": "測試內容"
            }
        }
        
        converter = TrendReportHTMLConverter(
            data=sample_data,
            category="technological",
            date_range="2025-10-01-2025-10-31"
        )
        
        html = converter.generate_html()
        
        # 檢查標籤配對
        assert html.count('<html') == html.count('</html>')
        assert html.count('<head>') == html.count('</head>')
        assert html.count('<body>') == html.count('</body>')
        assert html.count('<style>') == html.count('</style>')
    
    def test_no_inline_scripts(self):
        """測試不包含內聯腳本（安全性）"""
        sample_data = {
            "趨勢報告": "測試報告",
            "關鍵字": ["測試"],
            "主要趨勢1": {
                "標題": "測試趨勢",
                "<a>趨勢洞察": "測試內容"
            }
        }
        
        converter = TrendReportHTMLConverter(
            data=sample_data,
            category="technological",
            date_range="2025-10-01-2025-10-31"
        )
        
        html = converter.generate_html()
        
        # 不應該包含 JavaScript
        assert '<script' not in html.lower()
    
    def test_css_in_style_tag(self):
        """測試 CSS 包含在 style 標籤中"""
        sample_data = {
            "趨勢報告": "測試報告",
            "關鍵字": ["測試"],
            "主要趨勢1": {
                "標題": "測試趨勢",
                "<a>趨勢洞察": "測試內容"
            }
        }
        
        converter = TrendReportHTMLConverter(
            data=sample_data,
            category="technological",
            date_range="2025-10-01-2025-10-31"
        )
        
        html = converter.generate_html()
        
        # CSS 應該在 <style> 標籤內
        assert '<style>' in html
        assert '</style>' in html
        
        # 提取 style 標籤內容
        style_start = html.find('<style>')
        style_end = html.find('</style>')
        style_content = html[style_start:style_end]
        
        # CSS 應該包含基本樣式
        assert 'font-family' in style_content
        assert 'background' in style_content


class TestEdgeCases:
    """測試邊界情況"""
    
    def test_invalid_category_fallback(self):
        """測試無效類別時使用預設配置"""
        converter = TrendReportHTMLConverter(
            data={"趨勢報告": "測試", "關鍵字": []},
            category="invalid_category",
            date_range="2025-10-01-2025-10-31"
        )
        
        # 應該使用預設配置（business_and_investment）
        assert converter.config['title'] == CATEGORY_CONFIG['business_and_investment']['title']
    
    def test_invalid_custom_theme_fallback(self):
        """測試無效自訂主題時使用預設主題"""
        converter = TrendReportHTMLConverter(
            data={"趨勢報告": "測試", "關鍵字": []},
            category="technological",
            date_range="2025-10-01-2025-10-31",
            custom_theme="invalid_theme"
        )
        
        # 應該使用該類別的預設主題
        theme = converter.get_theme()
        assert theme == "blue-purple-gradient"
    
    def test_very_long_content(self):
        """測試非常長的內容"""
        long_text = "測試內容 " * 1000
        data = {
            "趨勢報告": long_text,
            "關鍵字": ["測試"],
            "主要趨勢1": {
                "標題": "測試",
                "<a>趨勢洞察": long_text
            }
        }
        
        converter = TrendReportHTMLConverter(
            data=data,
            category="technological",
            date_range="2025-10-01-2025-10-31"
        )
        
        # 應該能處理長內容
        html = converter.generate_html()
        assert long_text in html
