# 護照辨識系統

使用 Google Gemini API 進行護照文字影像辨識的 Python 系統。

## 功能特色

- ✅ 使用 Google Gemini API 進行高準確度的護照號碼辨識
- ✅ 支援單張圖片和批次辨識
- ✅ 自動驗證圖片大小（限制 15MB）
- ✅ 結構化的 JSON 格式輸出
- ✅ 完整的錯誤處理機制
- ✅ 符合 SOLID 設計原則
- ✅ 完整的 docstring 文件

## 系統需求

- Python 3.10 或更高版本
- 下列其中一種認證方式：
  - **gcloud 認證**（建議）
  - Google Gemini API 金鑰

## 安裝

1. 複製專案到本地：

```bash
git clone <repository-url>
cd <project-directory>
```

2. 安裝依賴套件：

```bash
pip install -r requirements.txt
```

3. 設定認證（選擇其中一種方式）：

**方式 1: 使用 gcloud 認證（建議）**

```bash
# 安裝 Google Cloud SDK
# 參考: https://cloud.google.com/sdk/docs/install

# 設定應用程式預設認證
gcloud auth application-default login
```

**方式 2: 使用 API 金鑰**

```bash
export GEMINI_API_KEY="your-api-key-here"
```

## 快速開始

### 使用 gcloud 認證（建議）

```python
from src.gemini_image_recognizer import GeminiImageRecognizer
from src.passport_recognition_controller import PassportRecognitionController

# 建立辨識器（使用 gcloud 認證）
recognizer = GeminiImageRecognizer()

# 建立控制器
controller = PassportRecognitionController(recognizer=recognizer)

# 辨識護照圖片
result = controller.recognize_passport("/path/to/passport.jpg")

print(f"護照號碼: {result.passport_number}")
print(f"信心度: {result.confidence}")
print(f"是否找到: {result.is_found()}")
```

### 使用 API 金鑰

```python
from src.gemini_image_recognizer import GeminiImageRecognizer
from src.passport_recognition_controller import PassportRecognitionController

# 建立辨識器（使用 API 金鑰）
recognizer = GeminiImageRecognizer(api_key="your-api-key")

# 建立控制器
controller = PassportRecognitionController(recognizer=recognizer)

# 辨識護照圖片
result = controller.recognize_passport("/path/to/passport.jpg")

print(f"護照號碼: {result.passport_number}")
print(f"信心度: {result.confidence}")
print(f"是否找到: {result.is_found()}")
```

### 批次辨識

```python
# 批次辨識多張圖片
image_paths = [
    "/path/to/passport1.jpg",
    "/path/to/passport2.jpg",
    "/path/to/passport3.jpg"
]

results = controller.batch_recognize_passports(image_paths)

for path, result in results.items():
    print(f"{path}: {result.passport_number}")
```

### 自訂提示詞

```python
custom_prompt = """
請辨識這張護照圖片中的護照號碼。
回傳 JSON 格式：
{
    "passport_number": "護照號碼",
    "confidence": "信心度"
}
"""

result = controller.recognize_passport(
    "/path/to/passport.jpg",
    custom_prompt=custom_prompt
)
```

## 專案結構

```
.
├── src/
│   ├── __init__.py
│   ├── gemini_image_recognizer.py      # Gemini API 互動模組
│   ├── passport_recognition_controller.py  # 辨識控制器
│   └── response_parser.py              # 回應解析器
├── example.py                          # 使用範例
├── requirements.txt                    # 專案依賴
├── README.md                          # 專案說明文件
├── 類別圖.md                           # 系統類別圖
├── 序列圖.md                           # 系統序列圖
└── 元件圖.md                           # 系統元件圖
```

## 核心元件

### GeminiImageRecognizer
負責與 Google Gemini API 互動，處理圖片讀取、驗證和辨識功能。

**主要功能：**
- 驗證圖片大小（不超過 15MB）
- 讀取圖片檔案
- 調用 Gemini API 進行辨識

### PassportRecognitionController
控制器類別，協調整個辨識流程。

**主要功能：**
- 管理辨識流程
- 設計格式化提示詞
- 整合辨識器和解析器
- 支援單張和批次辨識

### ResponseParser
解析 LLM 回傳的文字內容。

**主要功能：**
- 從文字中提取 JSON 內容
- 驗證 JSON 格式和欄位
- 建立結構化的結果物件

### PassportRecognitionResult
封裝護照辨識結果的資料類別。

**主要功能：**
- 儲存辨識結果
- 提供結果查詢方法
- 轉換為字典格式

## 錯誤處理

系統提供完整的錯誤處理機制：

- **FileNotFoundError**: 圖片檔案不存在
- **ValueError**: 圖片大小超過限制、參數驗證失敗、JSON 解析失敗
- **OSError**: 讀取圖片檔案失敗
- **RuntimeError**: Gemini API 調用失敗

所有錯誤都使用具體的錯誤類型，不使用籠統的 `Exception` 捕捉。

## 設計原則

本專案遵循以下設計原則：

### SOLID 原則
- **單一職責原則**: 每個類別只負責一個特定功能
- **開放封閉原則**: 可透過自訂提示詞和注入依賴擴展功能
- **介面隔離原則**: 各類別提供專門的介面
- **依賴反轉原則**: 控制器依賴抽象而非具體實作

### 程式碼規範
- 完整的 docstring 文件（包含 Args、Returns、Examples、Raises）
- 具體的錯誤類型捕捉
- 清晰的職責劃分
- 避免過度設計

## API 參考

詳細的 API 文件請參考各模組的 docstring。

## 系統圖表

- [類別圖](類別圖.md) - 展示系統的類別結構與關係
- [序列圖](序列圖.md) - 展示系統的執行流程
- [元件圖](元件圖.md) - 展示系統的元件架構

## 認證方式說明

本系統支援兩種認證方式：

### 1. gcloud 認證（建議）

使用 Google Cloud SDK 的應用程式預設認證，適合在開發環境和生產環境中使用。

**優點：**
- 無需管理 API 金鑰
- 更安全的認證機制
- 符合企業級安全標準
- 自動處理認證過期和更新

**設定方式：**
```bash
gcloud auth application-default login
```

**程式碼使用：**
```python
recognizer = GeminiImageRecognizer()  # 不需要傳入 api_key
```

### 2. API 金鑰

直接使用 API 金鑰進行認證，適合快速測試和簡單應用。

**使用方式：**
```python
recognizer = GeminiImageRecognizer(api_key="your-api-key")
```

## 注意事項

1. 圖片大小限制為 15MB
2. 支援的圖片格式：JPEG
3. 使用 gcloud 認證時，需先執行 `gcloud auth application-default login`
4. 使用 API 金鑰時，請妥善保管金鑰，不要提交到版本控制系統
5. 建議使用 gemini-1.5-flash 模型以獲得最佳效能

## 授權

MIT License

## 貢獻

歡迎提交 Issue 和 Pull Request。
