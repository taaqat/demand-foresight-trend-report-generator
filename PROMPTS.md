# Prompt 變數說明文件

本文件說明 `prompt_manager.py` 中所有 prompt 變數的名稱、用途及對應的檔案來源。

---

## 📁 檔案結構

所有 prompt 文字檔存放於 `prompts/` 目錄下：

```
prompts/
├── steep_step1_categorize.txt
├── steep_step2_categorize.txt
├── steep_step3_aggregate.txt
├── steep_step4_classify.txt
├── steep_step5_infer.txt
└── steep_step6_conclude.txt
```

---

## 🔧 STEEP 類別 Prompts

STEEP 分析流程用於產業趨勢報告生成，包含 6 個主要步驟：

### Step 1: 每日新聞 STEEP 分類
- **變數名稱**: `step1_prompt(date)`
- **類型**: 靜態方法（需要動態參數）
- **檔案來源**: `prompts/steep_step1_categorize.txt`
- **參數**: 
  - `date`: 日期字串（格式：YYYY-MM-DD）
- **用途**: 將每日新聞按 STEEP+B 框架分類
  - S - Social (社會)
  - T - Technological (科技)
  - E - Economic (經濟)
  - E - Environmental (環境)
  - P - Political (政治)
  - B - Business and Investment (投資)
- **輸入**: 原始新聞文本
- **輸出**: JSON 格式的分類結果，以日期為 key，每個類別包含 3-5 則重點新聞摘要
- **範例**: `PromptManager.STEEP.step1_prompt("2024-01-01")`

---

### Step 2: 每日新聞分類（首個版本）
- **變數名稱**: `step2_categorize_prompt(date)`
- **類型**: 靜態方法（需要動態參數）
- **檔案來源**: `prompts/steep_step2_categorize.txt`
- **參數**: 
  - `date`: 日期字串（格式：YYYY-MM-DD）
- **用途**: 對每日新聞進行詳細的 STEEP 分類並生成摘要
- **特點**: 
  - 每則新聞摘要 60-100 字
  - Technological 列出 4-5 則
  - Economic 列出 1-4 則（優先列舉央行、通膨、匯率相關）
  - 其他類別各 3-4 則
- **輸出**: 以日期為 key 的 JSON 格式分類結果
- **範例**: `PromptManager.STEEP.step2_categorize_prompt("2024-01-01")`

---

### Step 2: 三版本趨勢報告生成
- **變數名稱**: `step2_prompt(topic, ver)`
- **類型**: f-string 函數（需要動態參數）
- **檔案來源**: 內嵌於 `prompt_manager.py`（因需動態替換 `{topic}` 和 `{ver}`）
- **參數**:
  - `topic`: STEEP 主題類別（如 "Technological", "Economic"）
  - `ver`: 版本號（1-3）
- **用途**: 根據每月新聞生成三個版本的趨勢分析
- **輸出**: 
  - 每個主題 6-10 個趨勢標題（經濟類 4-5 個）
  - 每個趨勢包含 4-7 個代表事件
  - JSON 格式: `{"{topic}-v{ver}": {"趨勢標題": "...", "代表事件": [...]}}`

---

### Step 3: 合併三個版本
- **變數名稱**: `step3_prompt`
- **檔案來源**: `prompts/steep_step3_aggregate.txt`
- **用途**: 綜合三次趨勢分析結果，合併並整理最具代表性的趨勢
- **處理邏輯**:
  1. 列出所有趨勢標題（去重）
  2. 合併相似標題
  3. 按代表性和影響力排序
  4. 生成 200 字左右的趨勢洞察
  5. 提取 12-20 個關鍵字 Hashtag
- **輸出**: 至少 10 個主要趨勢，每個包含標題、洞察、關鍵詞

---

### Step 4: 事件分類回歸趨勢
- **變數名稱**: `step4_prompt`
- **檔案來源**: `prompts/steep_step4_classify.txt`
- **用途**: 將代表事件歸類到對應趨勢下，並進行關聯度分析
- **處理內容**:
  - 每個趨勢對應 3-4 個最具啟發性的代表事件
  - 每則事件分析 30-45 字
  - 標註事件與趨勢的關聯度（0-100%）
  - 關聯度低於 80% 的事件會被加粗標示
- **輸出**: JSON 格式，包含標題、洞察、關鍵詞、代表事件

---

### Step 5: 詳細推論生成
- **變數名稱**: `step5_prompt`
- **檔案來源**: `prompts/steep_step5_infer.txt`
- **用途**: 對每個趨勢進行深度分析和未來推論
- **分析維度**:
  - `<d>` 重要關係人（供給端、需求端）
  - `<e>` 缺口（至少 3 個，15-28 字）
  - `<f>` 未來產品或服務機會點（至少 3 個，18-28 字）
  - `<g>` 關鍵驅動因素（社會、政治、經濟、文化，18-28 字）
  - `<h>` 微弱信號（至少 3 個，18-28 字）
  - `<i>` 時間尺度（極短期/短期/中期/中長期/長期）
  - `<j>` 趨勢總結洞察（300 字以上）
- **輸出**: 完整的趨勢分析報告

---

### Step 6: 趨勢報告總結
- **變數名稱**: `step6_prompt`
- **檔案來源**: `prompts/steep_step6_conclude.txt`
- **用途**: 產出最終的趨勢摘要報告
- **內容要求**:
  - 250-400 字的趨勢摘要
  - 涵蓋各種面向，不過度聚焦單一事件
  - 採用文章形式（無換行分段）
  - 提取 50-80 個相關關鍵字
- **輸出**: JSON 格式，包含趨勢報告和關鍵字列表

---

## 🎯 SELF_SELECT 類別 Prompts

SELF_SELECT 流程用於使用者自選主題的趨勢分析：

### Step 1: 新聞摘要
- **變數名稱**: `step1_prompt`
- **類型**: lambda 函數
- **參數**: 
  - `keywords`: 關鍵字（未使用）
  - `batch`: 批次編號
- **用途**: 將一批新聞統整成重點摘要
- **輸出**: JSON 格式，每則新聞 60-100 字摘要

---

### Step 2: 三版本趨勢報告
- **變數名稱**: `step2_prompt`
- **類型**: lambda 函數
- **參數**:
  - `title`: 主題標題
  - `ver`: 版本號（1-3）
  - `additional`: 額外指示（預設 "無"）
- **用途**: 根據每月新聞生成趨勢分析（自選主題版本）
- **特點**: 至少 10 組趨勢，至多 12 組

---

### Step 3: 合併三版本
- **變數名稱**: `step3_prompt`
- **類型**: lambda 函數
- **參數**: `additional` - 額外指示（預設 "無"）
- **用途**: 綜合三次趨勢分析，至少產出 10 個趨勢

---

### Step 4: 事件分類
- **變數名稱**: `step4_prompt`
- **類型**: lambda 函數
- **參數**: `additional` - 額外指示（預設 "無"）
- **用途**: 將代表事件歸類到趨勢下

---

### Step 5: 推論生成
- **變數名稱**: `step5_prompt`
- **類型**: lambda 函數
- **參數**:
  - `cols`: 需要推論的欄位
  - `additional`: 額外指示
- **用途**: 進行指定維度的深度推論

---

### Step 6: 總結報告
- **變數名稱**: `step6_prompt`
- **類型**: lambda 函數
- **參數**: `additional` - 額外指示（預設 "無"）
- **用途**: 產出最終趨勢總結

---

## 🔍 其他工具 Prompts

### PDF 關鍵數據提取
- **變數名稱**: `get_key_data_from_pdf(topic, trend_report_json)`
- **類型**: 函數
- **用途**: 從研究報告中找出支持趨勢的關鍵數據或案例
- **輸出**: 每個趨勢對應的關鍵數據和案例（含來源頁數）

---

### HTML 簡報生成
- **變數名稱**: `gen_html_slides` (Others 類別)
- **用途**: 將 JSON 格式趨勢報告轉換成 HTML & CSS 網頁式簡報
- **輸出**: 完整的 HTML 程式碼（含 CSS 樣式）

---Prompt 模板與動態參數處理

1. **使用文字檔 + `.format()` 方法的 prompt**（如 `step1_prompt(date)`, `step2_categorize_prompt(date)`）：
   - Prompt 文字存放在 `.txt` 檔案中
   - 使用 `{date}` 作為佔位符
   - 在 `prompt_manager.py` 中載入為模板，透過靜態方法接收參數並用 `.format()` 替換
   - **優點**: 避免雙倍轉義，prompt 內容清晰易讀，易於維護
   
2. **使用 f-string 的 prompt**（如 `step2_prompt(topic, ver)`）：
   - 直接在 `prompt_manager.py` 中定義為 f-string 函數
   - 需要動態替換多個變數 `{topic}` 和 `{ver}`
   - **原因**: f-string 可以直接在字串中嵌入複雜邏輯
   
3. **Lambda 函數形式的 prompt**（SELF_SELECT 類別）：
   - 包含複雜的參數邏輯和預設值
   - 保持為 Python 函數更靈活

### 轉義規則差異

- **文字檔 + `.format()` 方法**：使用正常的 JSON 格式 `{ }`，在變數位置使用 `{date}`
- **f-string 中**：需要雙倍轉義 `{{{{ }}}}`

這就是為什麼將 prompt 抽取到文字檔搭配 `.format()` 可以避免雙倍轉義的問題！

### 實作範例

```python
# 文字檔內容 (steep_step1_categorize.txt)
{
"{date}": {
    "Social(社會)": "..."
}
}

# prompt_manager.py
with open('steep_step1_categorize.txt', 'r', encoding='utf-8') as f:
    _step1_prompt_template = f.read()

@staticmethod
def step1_prompt(date):
    return PromptManager.STEEP._step1_prompt_template.format(date=date)

## 🔄 更新記錄

### 2025-12-08
- 將 `step1_prompt` 和 `step2_categorize_prompt` 改為靜態方法，支援動態日期參數
- 修改對應的 `.txt` 檔案，將 `***輸入的日期***` 改為 `{date}` 佔位符
- 使用 `.format()` 方法進行參數替換，避免 f-string 的雙倍轉義問題
- 更新文件說明，新增實作範例

---

# 使用方式
prompt = PromptManager.STEEP.step1_prompt("2024-01-01")
# 結果會將 {date} 替換為 "2024-01-01"
```
- **文字檔中**：使用正常的 JSON 格式 `{ }` 
- **f-string 中**：需要雙倍轉義 `{{{{ }}}}`

這就是為什麼將 prompt 抽取到文字檔可以避免雙倍轉義的問題！

---

## 📊 Prompt 使用流程

### STEEP 分析完整流程：
```
原始新聞
    ↓
[Step 1] 每日分類 (step1_prompt)
    ↓
[Step 2] 三版本趨勢生成 (step2_prompt × 3)
    ↓
[Step 3] 合併版本 (step3_prompt)
    ↓
[Step 4] 事件分類 (step4_prompt)
    ↓
[Step 5] 深度推論 (step5_prompt)
    ↓
[Step 6] 總結報告 (step6_prompt)
    ↓
最終趨勢報告
```

---

最後更新：2025-12-08
