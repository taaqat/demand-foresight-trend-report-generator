# 
# *** HTML Converter: 將 JSON 趨勢報告直接轉換為 HTML (不使用 LLMs)
# 根據 STREAMLIT_改寫指南.md 實作

import re
from typing import Dict, Any, Optional
from .html_themes import THEMES, CATEGORY_CONFIG


class TrendReportHTMLConverter:
    """趨勢報告轉換器 - 將 JSON 轉換為 HTML（不使用 LLMs）"""
    
    def __init__(self, data: Dict[str, Any], category: str, date_range: str, custom_theme: Optional[str] = None):
        """
        初始化轉換器
        
        Args:
            data: JSON 趨勢報告資料
            category: 報告類別 (business_and_investment, political, etc.)
            date_range: 日期範圍字串 (e.g., "2025-10-01-2025-10-31")
            custom_theme: 自訂主題名稱（可選）
        """
        self.data = data
        self.category = category
        self.date_range = date_range
        self.config = CATEGORY_CONFIG.get(category, CATEGORY_CONFIG['business_and_investment'])
        self.custom_theme = custom_theme
    
    def get_theme(self) -> str:
        """取得使用的主題"""
        if self.custom_theme and self.custom_theme in THEMES:
            return self.custom_theme
        return self.config['default_theme']
    
    def get_theme_colors(self, theme: str):
        """取得主題顏色"""
        return THEMES[theme]['gradient']
    
    def generate_html(self) -> str:
        """生成完整的 HTML"""
        theme = self.get_theme()
        colors = self.get_theme_colors(theme)
        
        html = '<!DOCTYPE html>\n'
        html += '<html lang="zh-TW">\n'
        html += '<head>\n'
        html += self._generate_head(colors)
        html += '</head>\n'
        html += '<body>\n'
        html += self._generate_body()
        html += '</body>\n'
        html += '</html>'
        
        return html
    
    def _generate_head(self, colors):
        """生成 HTML head 區塊"""
        title = f"{self.config['title']} - {self.date_range}"
        
        head = '<meta charset="UTF-8">\n'
        head += '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        head += f'<title>{title}</title>\n'
        head += '<style>\n'
        head += self._generate_css(colors)
        head += '</style>\n'
        
        return head
    
    def _generate_css(self, colors):
        """生成 CSS 樣式"""
        css = f"""
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Microsoft JhengHei', 'PingFang TC', 'Noto Sans TC', Arial, sans-serif;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            line-height: 1.6;
            padding: 0;
            margin: 0;
        }}
        
        .container {{
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 60px 40px;
            border-radius: 20px;
            color: white;
            background: linear-gradient(135deg, {colors[0]}, {colors[1]});
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        }}
        
        .header h1 {{
            font-size: 2.8em;
            margin-bottom: 20px;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }}
        
        .header p {{
            font-size: 1.3em;
            opacity: 0.95;
            font-weight: 300;
        }}
        
        .summary-box, .summary, .overview {{
            background: white;
            padding: 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
            border-left: 5px solid {colors[0]};
        }}
        
        .summary-box h2, .summary h2, .overview h2 {{
            color: {colors[0]};
            margin-bottom: 20px;
            font-size: 2em;
            font-weight: 600;
        }}
        
        .summary-box p, .summary p, .overview p {{
            font-size: 1.1em;
            line-height: 1.8;
            color: #555;
        }}
        
        .keywords-section {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        }}
        
        .keywords-section h3 {{
            color: {colors[0]};
            margin-bottom: 20px;
            font-size: 1.5em;
        }}
        
        .keyword, .tag, .hashtag {{
            display: inline-block;
            background: linear-gradient(135deg, {colors[0]}, {colors[1]});
            color: white;
            padding: 8px 16px;
            margin: 5px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 500;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
        }}
        
        .trend-card {{
            background: white;
            padding: 40px;
            margin-bottom: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .trend-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        }}
        
        .trend-card h2 {{
            color: {colors[0]};
            font-size: 2em;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid {colors[1]};
            font-weight: 600;
        }}
        
        .trend-content {{
            font-size: 1.05em;
            color: #444;
        }}
        
        .trend-section {{
            margin-bottom: 30px;
        }}
        
        .trend-section h3 {{
            color: {colors[1]};
            font-size: 1.4em;
            margin-bottom: 15px;
            font-weight: 600;
        }}
        
        .trend-section p, .trend-section ul {{
            line-height: 1.8;
            color: #555;
        }}
        
        .trend-section ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        
        .trend-section li {{
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .trend-section li:last-child {{
            border-bottom: none;
        }}
        
        .event-item {{
            background: #f8f9fa;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 10px;
            border-left: 4px solid {colors[0]};
        }}
        
        .event-item strong {{
            color: {colors[0]};
            display: block;
            margin-bottom: 8px;
            font-size: 1.1em;
        }}
        
        .stakeholder-item {{
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
        }}
        
        .stakeholder-item strong {{
            color: {colors[1]};
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2em;
            }}
            
            .header p {{
                font-size: 1.1em;
            }}
            
            .trend-card {{
                padding: 25px;
            }}
            
            .trend-card h2 {{
                font-size: 1.5em;
            }}
            
            .container {{
                padding: 20px 10px;
            }}
        }}
        """
        
        return css
    
    def _generate_body(self):
        """生成 HTML body 區塊"""
        html = '<div class="container">\n'
        html += self._generate_header()
        html += self._generate_summary()
        html += self._generate_trends()
        html += '</div>\n'
        
        return html
    
    def _generate_header(self):
        """生成標題區塊"""
        title = self.config['title']
        # 將日期範圍格式化為更易讀的格式
        date_display = self.date_range.replace('-', ' / ')
        
        return f"""
        <div class="header">
            <h1>{title}</h1>
            <p>時間區間: {date_display}</p>
        </div>
        """
    
    def _generate_summary(self):
        """生成概述區塊"""
        summary_class = self.config['summary_class']
        summary_text = self.data.get('趨勢報告', '')
        keywords = self.data.get('關鍵字', [])
        
        html = f'<div class="{summary_class}">\n'
        html += '<h2>趨勢概述</h2>\n'
        html += f'<p>{summary_text}</p>\n'
        html += '</div>\n'
        
        # 顯示關鍵字（如果配置需要）
        if self.config['show_keywords'] and keywords:
            keyword_class = self.config['keyword_class']
            html += '<div class="keywords-section">\n'
            html += '<h3>關鍵字</h3>\n'
            for keyword in keywords:
                html += f'<span class="{keyword_class}">{keyword}</span>\n'
            html += '</div>\n'
        
        return html
    
    def _generate_trends(self):
        """生成所有趨勢卡片"""
        html = ''
        
        # 遍歷所有主要趨勢
        for i in range(1, 13):
            trend_key = f"主要趨勢{i}"
            if trend_key in self.data and isinstance(self.data[trend_key], dict):
                html += self._generate_trend_card(self.data[trend_key])
        
        return html
    
    def _generate_trend_card(self, trend: Dict[str, Any]):
        """生成單個趨勢卡片"""
        html = '<div class="trend-card">\n'
        html += f'<h2>{trend.get("標題", "")}</h2>\n'
        html += '<div class="trend-content">\n'
        
        # <a> 趨勢洞察
        if '<a>趨勢洞察' in trend:
            html += '<div class="trend-section">\n'
            html += '<h3>🔍 趨勢洞察</h3>\n'
            html += f'<p>{trend["<a>趨勢洞察"]}</p>\n'
            html += '</div>\n'
        
        # <b> Hashtag關鍵詞
        if '<b>Hashtag關鍵詞' in trend:
            html += '<div class="trend-section">\n'
            html += '<h3>#️⃣ Hashtag 關鍵詞</h3>\n'
            hashtags = trend['<b>Hashtag關鍵詞']
            if isinstance(hashtags, list):
                for tag in hashtags:
                    html += f'<span class="hashtag">#{tag}</span>\n'
            html += '</div>\n'
        
        # <c> 代表事件
        if '<c>代表事件' in trend:
            html += '<div class="trend-section">\n'
            html += '<h3>📰 代表事件</h3>\n'
            events = trend['<c>代表事件']
            if isinstance(events, list):
                for event in events:
                    if isinstance(event, dict):
                        html += '<div class="event-item">\n'
                        html += f'<strong>事件：</strong>{event.get("事件", "無資料")}<br>\n'
                        html += f'<strong>分析：</strong>{event.get("分析", "無資料")}<br>\n'
                        source = event.get('來源') or event.get('(來源', '無資料')
                        html += f'<strong>來源：</strong>{source}<br>\n'
                        html += f'<strong>關聯度：</strong>{event.get("關聯度", "無資料")}\n'
                        html += '</div>\n'
            html += '</div>\n'
        
        # <d> 重要關係人
        if '<d>重要關係人' in trend:
            html += '<div class="trend-section">\n'
            html += '<h3>👥 重要關係人</h3>\n'
            stakeholders = trend['<d>重要關係人']
            if isinstance(stakeholders, dict):
                for key, value in stakeholders.items():
                    html += f'<div class="stakeholder-item"><strong>{key}：</strong>{value}</div>\n'
            html += '</div>\n'
        
        # <e> 缺口
        if '<e>缺口' in trend:
            html += '<div class="trend-section">\n'
            html += '<h3>🔍 議題缺口</h3>\n'
            html += '<ul>\n'
            gaps = trend['<e>缺口']
            if isinstance(gaps, list):
                for gap in gaps:
                    html += f'<li>{gap}</li>\n'
            html += '</ul>\n'
            html += '</div>\n'
        
        # <f> 未來產品或服務機會點
        if '<f>未來產品或服務機會點' in trend:
            html += '<div class="trend-section">\n'
            html += '<h3>💡 未來產品或服務機會點</h3>\n'
            html += '<ul>\n'
            opportunities = trend['<f>未來產品或服務機會點']
            if isinstance(opportunities, list):
                for opp in opportunities:
                    html += f'<li>{opp}</li>\n'
            html += '</ul>\n'
            html += '</div>\n'
        
        # <g> 關鍵驅動因素
        if '<g>關鍵驅動因素' in trend:
            html += '<div class="trend-section">\n'
            html += '<h3>⚙️ 關鍵驅動因素</h3>\n'
            drivers = trend['<g>關鍵驅動因素']
            if isinstance(drivers, dict):
                for aspect, driver in drivers.items():
                    html += f'<div class="stakeholder-item"><strong>{aspect}：</strong>{driver}</div>\n'
            html += '</div>\n'
        
        # <h> 微弱信號
        if '<h>微弱信號' in trend:
            html += '<div class="trend-section">\n'
            html += '<h3>📡 微弱信號</h3>\n'
            html += '<ul>\n'
            signals = trend['<h>微弱信號']
            if isinstance(signals, list):
                for signal in signals:
                    html += f'<li>{signal}</li>\n'
            html += '</ul>\n'
            html += '</div>\n'
        
        # <i> 時間尺度
        if '<i>時間尺度' in trend:
            html += '<div class="trend-section">\n'
            html += '<h3>⏰ 時間尺度</h3>\n'
            html += f'<p>{trend["<i>時間尺度"]}</p>\n'
            html += '</div>\n'
        
        # <j> 趨勢總結洞察
        if '<j>趨勢總結洞察' in trend:
            html += '<div class="trend-section">\n'
            html += '<h3>📊 趨勢總結洞察</h3>\n'
            html += f'<p>{trend["<j>趨勢總結洞察"]}</p>\n'
            html += '</div>\n'
        
        html += '</div>\n'  # trend-content
        html += '</div>\n'  # trend-card
        
        return html
