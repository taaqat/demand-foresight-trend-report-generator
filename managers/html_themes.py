# HTML 主題配置
# 根據 STREAMLIT_改寫指南.md 定義的主題系統

THEMES = {
    'blue': {
        'name': '專業藍色',
        'gradient': ['#3498db', '#2980b9'],
        'description': '專業、商務風格',
        'icon': '💼'
    },
    'deep-purple': {
        'name': '深藍紫色',
        'gradient': ['#1a237e', '#283593'],
        'description': '正式、莊重風格',
        'icon': '🏛️'
    },
    'blue-purple-gradient': {
        'name': '藍紫漸變',
        'gradient': ['#6e8efb', '#a777e3'],
        'description': '科技、現代風格',
        'icon': '🚀'
    },
    'green-gold': {
        'name': '綠金色',
        'gradient': ['#11998e', '#38ef7d'],
        'description': '財富、成長風格',
        'icon': '💰'
    },
    'green': {
        'name': '自然綠色',
        'gradient': ['#56ab2f', '#a8e063'],
        'description': '環保、自然風格',
        'icon': '🌱'
    },
    'orange': {
        'name': '溫暖橙色',
        'gradient': ['#f2994a', '#f2c94c'],
        'description': '溫暖、友善風格',
        'icon': '🔶'
    },
    'purple-blue': {
        'name': '紫藍漸變',
        'gradient': ['#6a11cb', '#2575fc'],
        'description': '社交、活力風格',
        'icon': '💜'
    },
    'red-pink': {
        'name': '紅粉漸變',
        'gradient': ['#eb3349', '#f45c43'],
        'description': '熱情、動感風格',
        'icon': '❤️'
    },
    'teal-lime': {
        'name': '青綠漸變',
        'gradient': ['#0ba360', '#3cba92'],
        'description': '清新、活力風格',
        'icon': '🌊'
    },
    'sunset': {
        'name': '日落漸變',
        'gradient': ['#ff6b6b', '#feca57'],
        'description': '溫馨、浪漫風格',
        'icon': '🌅'
    }
}

CATEGORY_CONFIG = {
    'business_and_investment': {
        'title': '全球科技與商業趨勢報告',
        'summary_class': 'summary-box',
        'show_keywords': False,
        'keywords_location': None,
        'keyword_class': 'hashtag',
        'default_theme': 'blue',
        'gradient_header': False
    },
    'political': {
        'title': '全球政治趨勢報告',
        'summary_class': 'summary',
        'show_keywords': True,
        'keywords_location': 'separate_section',
        'keyword_class': 'keyword',
        'default_theme': 'deep-purple',
        'gradient_header': True
    },
    'technological': {
        'title': '人工智慧技術發展趨勢報告',
        'summary_class': 'summary',
        'show_keywords': True,
        'keywords_location': 'in_summary',
        'keyword_class': 'tag',
        'default_theme': 'blue-purple-gradient',
        'gradient_header': True
    },
    'economic': {
        'title': '全球經濟趨勢報告',
        'summary_class': 'overview',
        'show_keywords': True,
        'keywords_location': 'as_cloud',
        'keyword_class': 'keyword',
        'default_theme': 'green-gold',
        'gradient_header': True
    },
    'environmental': {
        'title': '全球環境趨勢報告',
        'summary_class': 'summary',
        'show_keywords': True,
        'keywords_location': 'in_summary',
        'keyword_class': 'tag',
        'default_theme': 'green',
        'gradient_header': True
    },
    'social': {
        'title': '全球社會趨勢報告',
        'summary_class': 'summary',
        'show_keywords': True,
        'keywords_location': 'in_summary',
        'keyword_class': 'tag',
        'default_theme': 'purple-blue',
        'gradient_header': True
    }
}
