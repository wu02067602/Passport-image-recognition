# 護照辨識專案

藉由讀取護照圖片辨識圖片上面的護照號碼、性別、生日、中文名字、英文名字。

## 專案說明

本專案使用 Google Gemini API 進行中華民國護照的圖像文字辨識，能夠自動辨識以下資訊：

- 中文名稱
- 英文名稱
- 國籍
- 護照號碼
- 性別
- 出生年月日
- 護照效期

## 專案結構

```
/workspace
├── src/                        # 主要程式碼
│   ├── __init__.py            # 套件初始化
│   ├── image_encoder.py       # 圖片編碼器
│   ├── vision_analyzer.py     # 圖像分析器
│   ├── result_parser.py       # 結果解析器
│   ├── prompt_templates.py    # 提示詞模板
│   └── passport_controller.py # 主控制器
├── example.py                  # 使用範例
├── requirements.txt            # 專案依賴
├── .gitignore                 # Git 忽略檔案
├── README.md                   # 專案說明
├── 類別圖.md                  # 系統類別圖
├── 序列圖.md                  # 系統序列圖
└── 元件圖.md                  # 系統元件圖
```

## 安裝

### 環境需求

- Python 3.10 或以上版本
- Google Gemini API 金鑰

### 安裝依賴

```bash
pip install -r requirements.txt
```

## 使用方式

### 1. 完整護照辨識

```python
from src import PassportController

# 初始化控制器
controller = PassportController(api_key="YOUR_GEMINI_API_KEY")

# 辨識整本護照
result = controller.recognize_passport("path/to/passport.jpg")

print(f"中文名稱: {result['中文名稱']}")
print(f"英文名稱: {result['英文名稱']}")
print(f"護照號碼: {result['護照號碼']}")
# ... 其他欄位
```

### 2. 單一欄位辨識

```python
from src import PassportController, PassportField

controller = PassportController(api_key="YOUR_GEMINI_API_KEY")

# 只辨識中文名稱
chinese_name = controller.recognize_single_field(
    "path/to/passport.jpg",
    PassportField.CHINESE_NAME
)
print(f"中文名稱: {chinese_name}")
```

### 3. 詳細使用範例

請參考 `example.py` 檔案以獲得完整的使用範例。

## 系統設計

### 架構設計

本專案遵循 SOLID 設計原則，採用模組化架構：

- **單一職責原則**：每個類別只負責一項功能
- **開放封閉原則**：可擴展新欄位而不需修改現有程式碼
- **依賴反轉原則**：高層模組不依賴低層模組的具體實作

### 核心模組

1. **PassportController**: 主控制器，協調所有模組
2. **ImageEncoder**: 處理圖片編碼和格式驗證
3. **VisionAnalyzer**: 呼叫 Gemini API 進行圖像理解
4. **ResultParser**: 解析 LLM 回應並結構化資料
5. **PromptTemplates**: 管理提示詞模板

詳細的系統設計請參考：
- [類別圖](./類別圖.md)
- [序列圖](./序列圖.md)
- [元件圖](./元件圖.md)

## 錯誤處理

本專案採用明確的錯誤處理機制：

- `FileNotFoundError`: 圖片檔案不存在
- `ValueError`: 圖片格式不支援或無法開啟
- `RuntimeError`: Gemini API 呼叫失敗
- `ParseError`: LLM 回應解析失敗

## 專案階段

### 一、辨識（已完成）

建立一個可以藉由操作 Controller 來進行圖像辨識，整體辨識流程比較人工。讓資料科學家單獨一個一個確認辨識結果。

### 二、自動調整提示詞（規劃中）

利用已經提供好的標籤進行提示詞自動調整，區分好訓練集、測試集，先在訓練集之中調整好提示詞後進入測試集測試，直到測試集的結果也很好為止。

## 注意事項

1. 需要有效的 Google Gemini API 金鑰
2. 支援的圖片格式：JPG、JPEG、PNG
3. 建議使用清晰、完整的護照圖片以獲得最佳辨識效果
4. API 呼叫會產生費用，請注意使用量

## 授權

本專案遵循專案規範開發，所有程式碼均包含完整的 docstring 和錯誤處理。