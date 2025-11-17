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
├── app.py                    # Flask API 入口
├── example.py                # BASE64 使用範例
├── main.py                   # 批次處理工具
├── requirements.txt          # 專案依賴
├── src/                      # 主要程式碼
│   ├── __init__.py           # 套件初始化
│   ├── passport_service.py   # BASE64 服務層
│   ├── vision_analyzer.py    # 圖像分析器
│   ├── result_parser.py      # 結果解析器
│   └── prompt_templates.py   # 提示詞模板
├── README.md                 # 專案說明
├── 類別圖.md                # 系統類別圖
├── 序列圖.md                # 系統序列圖
└── 元件圖.md                # 系統元件圖
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

### 1. 透過 PassportService 進行辨識

```python
from pathlib import Path
import base64

from src import PassportService

service = PassportService()
image_path = Path("path/to/passport.jpg")

image_bytes = image_path.read_bytes()
base64_image = base64.b64encode(image_bytes).decode("utf-8")

result = service.recognize_from_base64(base64_image)
print(f"中文名稱: {result.get('中文名稱')}")
print(f"護照號碼: {result.get('護照號碼')}")
```

> 提醒：範例中會先將檔案轉成 BASE64，再傳入服務層。更完整的示範請參考 `example.py`。

### 2. 呼叫 Flask API

```bash
curl -X POST http://localhost:5000/api/passport/recognize \
  -H "Content-Type: application/json" \
  -d '{"image": "BASE64_STRING"}'
```

### 3. 使用批次處理工具

```bash
python main.py --input ./passports --output ./results.csv
```

批次處理器會掃描目錄、將圖片轉為 BASE64 並呼叫 `PassportService`，最後寫入 CSV 檔案。

## 系統設計

### 架構設計

本專案遵循 SOLID 設計原則，採用模組化架構：

- **單一職責原則**：每個類別只負責一項功能
- **開放封閉原則**：可擴展新欄位而不需修改現有程式碼
- **依賴反轉原則**：高層模組不依賴低層模組的具體實作

### 核心模組

1. **PassportService**：處理 BASE64 圖片、呼叫 VisionAnalyzer，並整合 ResultParser
2. **PassportBatchProcessor**：掃描資料夾、轉換檔案為 BASE64、批次呼叫 PassportService
3. **VisionAnalyzer**：對每個欄位發送提示詞並呼叫 Gemini API 取得結果
4. **ResultParser**：解析 LLM JSON 回應並產出結構化資料
5. **PromptTemplates**：集中管理各欄位的提示詞模板

詳細的系統設計請參考：
- [類別圖](./類別圖.md)
- [序列圖](./序列圖.md)
- [元件圖](./元件圖.md)

## 錯誤處理

本專案採用明確的錯誤處理機制：

- `ValueError`：BASE64 字串解碼失敗、圖片格式不支援或無法辨識
- `RuntimeError`：呼叫 Gemini API 過程中發生錯誤
- `ParseError`：LLM 回應無法解析為合法 JSON
- `FileNotFoundError` / `IOError`：批次處理或範例程式在讀取本地檔案時發生問題

## 專案階段

### 一、辨識（已完成）

建立一個可以藉由操作 Controller 來進行圖像辨識，整體辨識流程比較人工。讓資料科學家單獨一個一個確認辨識結果。

### 二、自動調整提示詞（規劃中）

利用已經提供好的標籤進行提示詞自動調整，區分好訓練集、測試集，先在訓練集之中調整好提示詞後進入測試集測試，直到測試集的結果也很好為止。

## 注意事項

1. 需要有效的 Google Gemini API 金鑰
2. 支援的圖片格式：JPG、JPEG、PNG、WEBP
3. 建議使用清晰、完整的護照圖片以獲得最佳辨識效果
4. API 呼叫會產生費用，請注意使用量

## 授權

本專案遵循專案規範開發，所有程式碼均包含完整的 docstring 和錯誤處理。