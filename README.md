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

- Python 3.14 或以上版本

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

> 提醒：範例中會先將檔案轉成 BASE64，再傳入服務層。

### 2. 呼叫 Flask API

#### 單張辨識

```bash
# 本地端
curl -X POST http://localhost:8080/api/passport/recognize \
  -H "Content-Type: application/json" \
  -d '{"image": "BASE64_STRING"}'

# 雲端佈署
curl -X POST https://sit-passport-recog-data-api.colatour.org/api/passport/recognize \
  -H "Content-Type: application/json" \
  -d '{"image": "BASE64_STRING"}'
```

#### 批次辨識

```bash
# 本地端
curl -X POST http://localhost:8080/api/passport/recognize/batch \
  -H "Content-Type: application/json" \
  -d '{"images": ["BASE64_STRING_1", "BASE64_STRING_2", "BASE64_STRING_3"]}'

# 雲端佈署
curl -X POST https://sit-passport-recog-data-api.colatour.org/api/passport/recognize/batch \
  -H "Content-Type: application/json" \
  -d '{"images": ["BASE64_STRING_1", "BASE64_STRING_2", "BASE64_STRING_3"]}'
```

> 請將 `BASE64_STRING` 替換為實際的 BASE64 編碼圖片字串。
> 批次辨識每次最多可同時處理 20 張圖片，超過則會分批次處理。




## API 文件

### 基礎資訊

- **Base URL (本地端)**: `http://localhost:8080`
- **Base URL (雲端佈署)**: `https://sit-passport-recog-data-api.colatour.org`
- **Content-Type**: `application/json`
- **API 版本**: v1

### 端點列表

#### 1. 護照辨識

辨識護照圖片中的資訊，包括中文名稱、英文名稱、國籍、護照號碼、性別、出生年月日、護照效期等。

**端點**: `POST /api/passport/recognize`

**請求標頭**:
```
Content-Type: application/json
```

**請求參數**:

| 參數名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| image | string | 是 | BASE64 編碼的圖片字串（不含 data URI 前綴） |

**請求範例**:

```bash
curl -X POST http://localhost:8080/api/passport/recognize \
  -H "Content-Type: application/json" \
  -d '{
    "image": "iVBORw0KGgoAAAANSUhEUgAA..."
  }'
```

**成功回應** (HTTP 200):

```json
{
  "success": true,
  "data": {
    "中文名稱": "張三",
    "英文名稱": "CHANG, SAN",
    "國籍": {
      "name": "中華民國",
      "code": "TWN"
    },
    "護照號碼": "123456789",
    "性別": "男",
    "出生年月日": "1990-01-01",
    "護照效期": "2030-12-31"
  }
}
```

**回應欄位說明**:

| 欄位名稱 | 類型 | 說明 |
|---------|------|------|
| success | boolean | 請求是否成功 |
| data | object | 辨識結果資料 |
| data.中文名稱 | string \| null | 護照上的中文姓名（可能為 null） |
| data.英文名稱 | string | 護照上的英文姓名 （可能為 null）|
| data.國籍 | object | 國籍資訊 |
| data.國籍.name | string | 國籍名稱 （可能為 null）|
| data.國籍.code | string | 國籍代碼（ISO 3166-1 alpha-3） （可能為 null）|
| data.護照號碼 | string | 護照號碼 （可能為 null）|
| data.性別 | string | 性別（"M" 或 "F"） （可能為 null）|
| data.出生年月日 | string | 出生日期（格式：YYYY-MM-DD） （可能為 null）|
| data.護照效期 | string | 護照到期日（格式：YYYY-MM-DD） （可能為 null）|

**錯誤回應**:

**400 Bad Request** - 請求參數錯誤

```json
{
  "success": false,
  "error": "請求參數錯誤: BASE64 解碼失敗: ..."
}
```

可能的原因：
- 缺少 `image` 欄位
- `image` 欄位為空或非字串類型
- BASE64 字串格式錯誤
- 圖片格式不支援（僅支援 JPG、JPEG、PNG、WEBP）

**500 Internal Server Error** - 伺服器錯誤

```json
{
  "success": false,
  "error": "辨識服務錯誤: ..."
}
```

可能的原因：
- 網路連線問題
- 圖片無法辨識

#### 2. 批次護照辨識

一次辨識多張護照圖片中的資訊，支援大量批次處理。每批次最多同時處理 20 張圖片，超過則依序分批處理。

**端點**: `POST /api/passport/recognize/batch`

**請求標頭**:
```
Content-Type: application/json
```

**請求參數**:

| 參數名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| images | array | 是 | BASE64 編碼的圖片字串陣列 |

**請求範例**:

```bash
curl -X POST http://localhost:8080/api/passport/recognize/batch \
  -H "Content-Type: application/json" \
  -d '{
    "images": [
      "iVBORw0KGgoAAAANSUhEUgAA...",
      "iVBORw0KGgoAAAANSUhEUgBB...",
      "iVBORw0KGgoAAAANSUhEUgCC..."
    ]
  }'
```

**成功回應** (HTTP 200):

```json
{
  "success": true,
  "data": {
    "results": [
      {
        "index": 0,
        "success": true,
        "data": {
          "中文名稱": "張三",
          "英文名稱": "CHANG, SAN",
          "國籍": {"name": "REPUBLIC OF CHINA", "code": "TWN"},
          "護照號碼": "123456789",
          "性別": "M",
          "出生年月日": "1990-01-01",
          "護照效期": "2030-12-31"
        }
      },
      {
        "index": 1,
        "success": true,
        "data": {
          "中文名稱": "李四",
          "英文名稱": "LI, SI",
          "國籍": {"name": "REPUBLIC OF CHINA", "code": "TWN"},
          "護照號碼": "987654321",
          "性別": "F",
          "出生年月日": "1985-06-15",
          "護照效期": "2028-06-14"
        }
      },
      {
        "index": 2,
        "success": false,
        "error": "請求參數錯誤: BASE64 解碼失敗: ..."
      }
    ],
    "total": 3,
    "successful": 2,
    "failed": 1
  }
}
```

**回應欄位說明**:

| 欄位名稱 | 類型 | 說明 |
|---------|------|------|
| success | boolean | 整體請求是否成功 |
| data.results | array | 每張圖片的辨識結果陣列 |
| data.results[].index | number | 圖片在原始陣列中的索引 |
| data.results[].success | boolean | 該圖片辨識是否成功 |
| data.results[].data | object | 辨識成功時的護照資料（同單張辨識格式） |
| data.results[].error | string | 辨識失敗時的錯誤訊息 |
| data.total | number | 總處理圖片數量 |
| data.successful | number | 成功辨識的圖片數量 |
| data.failed | number | 辨識失敗的圖片數量 |

**錯誤回應**:

**400 Bad Request** - 請求參數錯誤

```json
{
  "success": false,
  "error": "images 欄位必須為陣列"
}
```

可能的原因：
- 缺少 `images` 欄位
- `images` 欄位不是陣列
- `images` 陣列為空
- 陣列中包含非字串或空字串元素

#### 3. 健康檢查

檢查 API 服務是否正常運行。

**端點**: `GET /health`

**請求範例**:

```bash
curl http://localhost:8080/health
```

**成功回應** (HTTP 200):

```json
{
  "status": "healthy"
}
```

### 錯誤碼說明

| HTTP 狀態碼 | 說明 |
|------------|------|
| 200 | 請求成功 |
| 400 | 請求參數錯誤（如缺少必要欄位、格式錯誤等） |
| 500 | 伺服器內部錯誤（如 API 呼叫失敗、解析錯誤等） |

### 使用注意事項

1. **圖片格式要求**：
   - 支援格式：JPG、JPEG、PNG、WEBP
   - 建議圖片清晰、完整，避免模糊或部分遮擋
   - BASE64 編碼時不需要包含 `data:image/jpeg;base64,` 等前綴

2. **BASE64 編碼範例**：

```python
import base64

# 讀取圖片檔案
with open("passport.jpg", "rb") as f:
    image_bytes = f.read()

# 轉換為 BASE64 字串
base64_string = base64.b64encode(image_bytes).decode("utf-8")

# 使用於 API 請求
import requests

response = requests.post(
    "http://localhost:8080/api/passport/recognize",
    json={"image": base64_string}
)
```

3. **API 限制**：
   - 建議實作請求頻率限制和錯誤重試機制，以避免頻繁呼叫導致的壅塞狀況
   - 單張辨識建議呼叫頻率為一秒至多 1 次
   - 批次辨識每次最多同時處理 20 張圖片，超過會自動分批處理

4. **回應時間**：
   - 單張辨識：約 15~30 秒
   - 批次辨識：取決於圖片數量，每批次 20 張約需 15~30 秒（因並發處理）
   - 時間取決於圖片大小、網路狀況

## 系統設計


### 核心模組

1. **PassportService**：處理 BASE64 圖片、呼叫 VisionAnalyzer，並整合 ResultParser
2. **VisionAnalyzer**：對每個欄位發送提示詞並呼叫 Gemini API 取得結果
3. **ResultParser**：解析 LLM JSON 回應並產出結構化資料
4. **PromptTemplates**：集中管理各欄位的提示詞模板

詳細的系統設計請參考：
- [類別圖](./類別圖.md)
- [序列圖](./序列圖.md)
- [元件圖](./元件圖.md)

## 錯誤處理

本專案採用明確的錯誤處理機制：

- `ValueError`：BASE64 字串解碼失敗、圖片格式不支援或無法辨識
- `RuntimeError`：呼叫 Gemini API 過程中發生錯誤
- `ParseError`：LLM 回應無法解析為合法 JSON
