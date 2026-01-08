# HTML 轉換功能說明

## 概述

此功能提供兩種方式將 JSON 趨勢報告轉換為 HTML：
1. **直接轉換**（預設）：使用 Python 程式碼直接生成 HTML，無需 LLMs
2. **LLMs 轉換**：使用 AI 模型生成 HTML（原有功能）

## Feature Flag

在 `managers/constants.py` 中定義：

```python
FEATURE_FLAGS = {
    'use_llms_convert_json_to_html': False  # 預設使用直接轉換
}
```

- **False**（預設）：使用直接轉換，快速且節省成本
- **True**：使用 LLMs 轉換，更靈活但需要 API 調用

## 新增檔案

### 1. `managers/html_themes.py`
定義 HTML 主題配色和類別配置：
- **10 種主題配色**：藍色、紫色、綠色、橙色等
- **6 種類別配置**：商業、政治、科技、經濟、環境、社會

### 2. `managers/html_converter.py`
核心轉換邏輯：
- `TrendReportHTMLConverter` 類別
- 將 JSON 資料轉換為美觀的 HTML 網頁
- 支援所有趨勢報告欄位（<a> ~ <j>）

### 3. `managers/constants.py`
新增 Feature Flags 配置

## 修改檔案

### 1. `managers/export_manager.py`
新增 `create_html()` 方法：
```python
@staticmethod
def create_html(topic: str, data: Dict[str, Any], start_date: str, end_date: str, 
               custom_theme: Optional[str] = None) -> str:
    """將 JSON 趨勢報告轉換為 HTML"""
```

### 2. `pages/page_steep.py`
更新兩個 HTML 生成位置：
- 主要報告生成流程（step3）
- HTML 簡報補做功能（html_slide_補做）

## 使用方式

### 方式 1：直接轉換（預設）

```python
from managers.export_manager import ExportManager

html_content = ExportManager.SELF_SELECT.create_html(
    topic='technological',
    data=json_data,
    start_date='2025-10-01',
    end_date='2025-10-31',
    custom_theme='blue-purple-gradient'  # 可選
)
```

### 方式 2：切換為 LLMs 轉換

在 `managers/constants.py` 中修改：
```python
FEATURE_FLAGS = {
    'use_llms_convert_json_to_html': True  # 啟用 LLMs 轉換
}
```

## 主題配色

可用主題（定義於 `html_themes.py`）：

| 主題名稱 | 說明 | 預設類別 |
|---------|------|----------|
| `blue` | 專業藍色 💼 | business_and_investment |
| `deep-purple` | 深藍紫色 🏛️ | political |
| `blue-purple-gradient` | 藍紫漸變 🚀 | technological |
| `green-gold` | 綠金色 💰 | economic |
| `green` | 自然綠色 🌱 | environmental |
| `purple-blue` | 紫藍漸變 💜 | social |
| `orange` | 溫暖橙色 🔶 | - |
| `red-pink` | 紅粉漸變 ❤️ | - |
| `teal-lime` | 青綠漸變 🌊 | - |
| `sunset` | 日落漸變 🌅 | - |

## 類別配置

每個類別都有專屬配置（定義於 `html_themes.py`）：

```python
CATEGORY_CONFIG = {
    'business_and_investment': {
        'title': '全球科技與商業趨勢報告',
        'default_theme': 'blue',
        'show_keywords': False,
        ...
    },
    'technological': {
        'title': '人工智慧技術發展趨勢報告',
        'default_theme': 'blue-purple-gradient',
        'show_keywords': True,
        ...
    },
    ...
}
```

## HTML 輸出結構

生成的 HTML 包含：

### 1. 標題區塊
- 報告標題
- 時間區間

### 2. 趨勢概述
- 趨勢報告文字
- 關鍵字標籤（視類別配置）

### 3. 主要趨勢卡片（1-12）
每個趨勢包含：
- 🔍 趨勢洞察
- #️⃣ Hashtag 關鍵詞
- 📰 代表事件
- 👥 重要關係人
- 🔍 議題缺口
- 💡 未來產品或服務機會點
- ⚙️ 關鍵驅動因素
- 📡 微弱信號
- ⏰ 時間尺度
- 📊 趨勢總結洞察

## 優點比較

### 直接轉換（預設）
✅ **優點**：
- 快速生成，無 API 延遲
- 節省 LLMs 成本
- 樣式一致性高
- 可預測的輸出
- 易於維護和調整

❌ **缺點**：
- 樣式較為固定
- 需要程式碼修改來調整版面

### LLMs 轉換
✅ **優點**：
- 可能產生更有創意的版面
- 可以接受自然語言指令調整

❌ **缺點**：
- 需要 API 調用成本
- 生成時間較長
- 輸出可能不一致
- 需要提示詞工程

## 技術細節

### 響應式設計
- 支援桌面和行動裝置
- 使用 CSS media queries
- 適應不同螢幕尺寸

### CSS 特性
- 漸層背景
- 卡片陰影效果
- Hover 動畫
- 圓角邊框
- 專業排版

### 相容性
- 支援所有現代瀏覽器
- UTF-8 編碼
- 中文字型優化

## 測試範例

在 `steep-json-to-html/examples/` 目錄中有範例 JSON 檔案可供測試：

```
examples/
├── 2025-10/
│   ├── business_and_investment_trend_report_2025-10-01-2025-10-31.json
│   ├── technological_trend_report_2025-10-01-2025-10-31.json
│   └── ...
└── 2025-11/
    └── ...
```

## 故障排除

### 問題：HTML 無法顯示中文
**解決**：確認 HTML 包含 `<meta charset="UTF-8">`

### 問題：主題顏色未套用
**解決**：檢查類別名稱是否正確，應為以下之一：
- `business_and_investment`
- `political`
- `technological`
- `economic`
- `environmental`
- `social`

### 問題：想切換回 LLMs 轉換
**解決**：在 `managers/constants.py` 中設定：
```python
FEATURE_FLAGS = {
    'use_llms_convert_json_to_html': True
}
```

## 未來擴展

可能的改進方向：
1. 支援更多主題配色
2. 允許使用者自訂 CSS
3. 加入圖表視覺化
4. 支援匯出為 PDF
5. 多語言支援

## 參考文件

- [STREAMLIT_改寫指南.md](steep-json-to-html/docs/STREAMLIT_改寫指南.md)
- [JSON_to_HTML_轉換規則.md](steep-json-to-html/docs/JSON_to_HTML_轉換規則.md)

---

**最後更新**：2026-01-08
**版本**：1.0
