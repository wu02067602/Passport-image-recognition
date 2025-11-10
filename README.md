# 護照辨識專案

藉由讀取護照圖片辨識圖片上面的護照號碼、性別、生日、中文名字、英文名字。

## 專案簡介

本專案使用 Google Gemini API 進行護照影像辨識，提供完整的 OCR 和資訊擷取功能。系統採用模組化設計，遵循 SOLID 原則，具有高度可擴展性和可維護性。

## 功能特色

- ✅ **護照資訊辨識**: 自動識別護照號碼、性別、生日、中文姓名、英文姓名
- ✅ **圖片驗證**: 自動檢查圖片檔案存在性與大小限制 (15MB)
- ✅ **多格式解析**: 支援 JSON、鍵值對等多種回應格式
- ✅ **彈性設計**: 支援自訂提示詞，可針對不同需求調整
- ✅ **SOLID 原則**: 遵循物件導向設計原則，易於擴展和測試
- ✅ **完整文檔**: 提供類別圖、元件圖、序列圖等技術文件

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設定 API Key

```bash
export GEMINI_API_KEY="your_api_key_here"
```

### 3. 執行範例

```python
import os
from src.models.image_recognizer import ImageRecognizer
from src.controllers.passport_recognition_controller import PassportRecognitionController

# 初始化
api_key = os.getenv('GEMINI_API_KEY')
recognizer = ImageRecognizer(api_key=api_key)
controller = PassportRecognitionController(recognizer=recognizer)

# 執行辨識
passport_info = controller.recognize_passport("path/to/passport.jpg")

# 顯示結果
print(f"護照號碼: {passport_info.passport_number}")
print(f"性別: {passport_info.gender}")
print(f"生日: {passport_info.birth_date}")
print(f"中文姓名: {passport_info.chinese_name}")
print(f"英文姓名: {passport_info.english_name}")
```

完整範例請參考 `example.py`。

## 專案結構

```
workspace/
├── src/                          # 主要原始碼
│   ├── controllers/              # 控制器層
│   │   └── passport_recognition_controller.py
│   ├── interfaces/               # 抽象介面層
│   │   ├── recognizer_interface.py
│   │   └── parser_interface.py
│   ├── models/                   # 模型層
│   │   └── image_recognizer.py
│   └── parsers/                  # 解析器層
│       └── response_parser.py
├── example.py                    # 使用範例
├── requirements.txt              # 依賴套件
├── README.md                     # 專案說明 (本文件)
├── 類別圖.md                     # 類別圖文件
├── 元件圖.md                     # 元件圖文件
└── 序列圖.md                     # 序列圖文件
```

## 系統架構

### 核心元件

1. **ImageRecognizer**: 影像辨識器，負責與 Gemini API 互動
2. **ResponseParser**: 回應解析器，負責解析 LLM 回應為結構化資料
3. **PassportRecognitionController**: 控制器，協調辨識和解析流程
4. **PassportInfo**: 資料類別，儲存護照資訊

### 設計原則

- **單一職責原則 (SRP)**: 每個類別只有一個變更的理由
- **開放封閉原則 (OCP)**: 對擴展開放，對修改封閉
- **里氏替換原則 (LSP)**: 可用子類別替換父類別
- **介面隔離原則 (ISP)**: 介面精簡，只定義必要方法
- **依賴反轉原則 (DIP)**: 依賴抽象而非具體實作

詳細設計請參考 `類別圖.md`、`元件圖.md`、`序列圖.md`。

## API 使用說明

### PassportRecognitionController

#### recognize_passport()
辨識護照並返回結構化資料。

```python
passport_info = controller.recognize_passport(
    image_path="path/to/passport.jpg",
    custom_prompt=None  # 可選：自訂提示詞
)
```

**返回**: `PassportInfo` 物件

#### recognize_passport_raw()
辨識護照並返回原始 LLM 回應。

```python
raw_response = controller.recognize_passport_raw(
    image_path="path/to/passport.jpg",
    custom_prompt=None  # 可選：自訂提示詞
)
```

**返回**: 字串格式的原始回應

### PassportInfo

資料類別，包含以下欄位：
- `passport_number`: 護照號碼
- `gender`: 性別
- `birth_date`: 生日
- `chinese_name`: 中文姓名
- `english_name`: 英文姓名
- `raw_response`: 原始 LLM 回應

方法：
- `to_dict()`: 轉換為字典格式

## 錯誤處理

### ImageSizeError
圖片大小超過 15MB 時拋出。

### ImageNotFoundError
圖片檔案不存在時拋出。

### 範例

```python
from src.models.image_recognizer import ImageSizeError, ImageNotFoundError

try:
    passport_info = controller.recognize_passport("passport.jpg")
except ImageNotFoundError as e:
    print(f"檔案不存在: {e}")
except ImageSizeError as e:
    print(f"檔案太大: {e}")
except Exception as e:
    print(f"其他錯誤: {e}")
```

## 自訂提示詞

系統提供預設的 JSON 格式提示詞，但您可以根據需求自訂：

```python
custom_prompt = """
請辨識此護照圖片中的護照號碼。
格式: 護照號碼: [號碼]
"""

result = controller.recognize_passport_raw(
    "passport.jpg",
    custom_prompt=custom_prompt
)
```

## 專案階段

### 一、辨識 ✅ (已完成)

建立一個可以藉由操作 Controller 來進行圖像辨識，整體辨識流程比較人工。讓資料科學家單獨一個一個確認辨識結果。

**已實現功能**:
- ✅ 影像辨識核心功能
- ✅ 多格式解析器
- ✅ 控制器協調機制
- ✅ 錯誤處理機制
- ✅ SOLID 原則重構
- ✅ 完整技術文件

### 二、自動調整提示詞 (規劃中)

利用已經提供好的標籤進行提示詞自動調整，區分好訓練集、測試集，先在訓練集之中調整好提示詞後進入測試集測試，直到測試集的結果也很好為止。

## 擴展性

### 新增其他辨識引擎

實作 `IImageRecognizer` 介面：

```python
from src.interfaces.recognizer_interface import IImageRecognizer

class GPT4VisionRecognizer(IImageRecognizer):
    def recognize(self, image_path: str, prompt: str) -> str:
        # 實作 GPT-4 Vision 辨識
        pass
```

### 新增其他解析策略

實作 `IResponseParser` 介面：

```python
from src.interfaces.parser_interface import IResponseParser

class XMLResponseParser(IResponseParser):
    def parse(self, response_text: str) -> PassportInfo:
        # 實作 XML 解析
        pass
```

## 依賴套件

- `google-generativeai` (>= 0.3.0): Google Gemini API SDK
- Python 標準函式庫: `pathlib`, `base64`, `json`, `re`, `dataclasses`, `typing`, `abc`

## 授權

本專案為內部開發專案。

## 貢獻

如有任何問題或建議，請聯繫開發團隊。