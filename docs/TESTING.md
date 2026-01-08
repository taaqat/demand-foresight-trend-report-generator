# 測試指南

## 快速開始

### 方式 1: 使用 pytest 命令（推薦）

```bash
# 執行所有測試
pytest

# 詳細輸出
pytest -v

# 超詳細輸出（顯示每個測試的詳細信息）
pytest -vv

# 只執行特定測試文件
pytest tests/test_html_converter.py

# 只執行特定測試類別
pytest tests/test_html_converter.py::TestTrendReportHTMLConverter

# 只執行特定測試函數
pytest tests/test_html_converter.py::TestTrendReportHTMLConverter::test_initialization

# 使用關鍵字過濾測試
pytest -k "test_initialization"

# 執行測試並顯示代碼覆蓋率
pytest --cov=managers --cov-report=term-missing

# 生成 HTML 覆蓋率報告
pytest --cov=managers --cov-report=html
# 然後打開 htmlcov/index.html 查看報告
```

### 方式 2: 使用 Makefile（更簡單）

```bash
# 執行所有測試
make test

# 詳細輸出
make test-verbose

# 顯示覆蓋率
make test-coverage

# 生成 HTML 覆蓋率報告
make test-html

# 清理緩存文件
make clean
```

### 方式 3: 使用 Python 腳本

```bash
# 執行所有測試
python run_tests.py

# 詳細模式
python run_tests.py -v

# 執行特定測試
python run_tests.py tests/test_html_converter.py
```

## 安裝測試依賴

```bash
pip install pytest pytest-cov
```

或者安裝所有依賴：

```bash
pip install -r requirements.txt
```

## 測試配置

測試配置定義在 `pytest.ini` 文件中：

- 測試目錄: `tests/`
- 測試文件: `test_*.py`
- 測試類: `Test*`
- 測試函數: `test_*`

## 編寫測試

### 基本測試結構

```python
import pytest
from managers.html_converter import TrendReportHTMLConverter

def test_example():
    """測試範例"""
    result = some_function()
    assert result == expected_value
```

### 使用 Fixtures

```python
@pytest.fixture
def sample_data():
    """共用測試資料"""
    return {
        "趨勢報告": "測試報告",
        "關鍵字": ["測試"]
    }

def test_with_fixture(sample_data):
    """使用 fixture 的測試"""
    assert "趨勢報告" in sample_data
```

### 參數化測試

```python
@pytest.mark.parametrize("category,expected", [
    ("technological", "人工智慧技術發展趨勢報告"),
    ("economic", "全球經濟趨勢報告"),
])
def test_categories(category, expected):
    """測試多個參數組合"""
    # 測試邏輯
    pass
```

## 測試覆蓋率

### 查看覆蓋率報告

```bash
# 終端機輸出
pytest --cov=managers --cov-report=term-missing

# 生成 HTML 報告
pytest --cov=managers --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### 覆蓋率目標

我們的目標是維持以下覆蓋率：
- 整體覆蓋率: > 80%
- 核心模組 (html_converter.py): > 90%

## 持續整合

在 CI/CD 環境中執行測試：

```bash
# 安裝依賴
pip install -r requirements.txt

# 執行測試並生成覆蓋率報告
pytest --cov=managers --cov-report=xml --cov-report=term

# 檢查測試結果
if [ $? -eq 0 ]; then
    echo "所有測試通過"
else
    echo "測試失敗"
    exit 1
fi
```

## 常見問題

### Q: 如何只執行失敗的測試？
```bash
pytest --lf  # last failed
```

### Q: 如何只執行新失敗的測試？
```bash
pytest --ff  # failed first
```

### Q: 如何在第一個失敗時停止？
```bash
pytest -x
```

### Q: 如何顯示所有輸出（包括 print）？
```bash
pytest -s
```

### Q: 如何並行執行測試？
```bash
# 先安裝 pytest-xdist
pip install pytest-xdist

# 使用多核心執行
pytest -n auto
```

## pytest 實用選項

| 選項 | 說明 |
|------|------|
| `-v, --verbose` | 詳細輸出 |
| `-vv` | 超詳細輸出 |
| `-q, --quiet` | 安靜模式 |
| `-s` | 顯示 print 輸出 |
| `-x` | 第一個失敗時停止 |
| `--lf` | 只執行上次失敗的測試 |
| `--ff` | 先執行失敗的測試 |
| `-k EXPRESSION` | 使用表達式過濾測試 |
| `--markers` | 顯示所有標記 |
| `--collect-only` | 只收集測試，不執行 |
| `--cov` | 顯示覆蓋率 |
| `--cov-report` | 覆蓋率報告格式 |

## 最佳實踐

1. **測試命名**: 使用描述性的名稱
   ```python
   def test_converter_handles_missing_optional_fields():
       # 清楚表達測試目的
       pass
   ```

2. **AAA 模式**: Arrange, Act, Assert
   ```python
   def test_example():
       # Arrange - 準備測試資料
       data = {"key": "value"}
       
       # Act - 執行測試動作
       result = process(data)
       
       # Assert - 驗證結果
       assert result == expected
   ```

3. **獨立性**: 每個測試應該獨立，不依賴其他測試

4. **可讀性**: 測試應該易於理解和維護

5. **覆蓋範圍**: 測試正常情況、邊界情況和錯誤情況

## 相關文件

- [pytest.ini](../pytest.ini) - pytest 配置
- [Makefile](../Makefile) - 快捷命令
- [run_tests.py](../run_tests.py) - Python 測試腳本
- [requirements.txt](../requirements.txt) - 依賴套件

---

**最後更新**: 2026-01-08
