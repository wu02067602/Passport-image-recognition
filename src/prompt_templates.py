"""提示詞模板模組

此模組定義護照辨識所需的提示詞枚舉和模板。
"""

from enum import Enum


class PassportField(Enum):
    """護照欄位枚舉
    
    定義護照中需要辨識的各個欄位類型。
    """
    CHINESE_NAME = "Chinese_Name"
    ENGLISH_NAME = "English_Name"
    NATIONALITY = "Nationality"
    PASSPORT_NUMBER = "Passport_Number"
    SEX = "Sex"
    DATE_OF_BIRTH = "Date_of_Birth"
    DATE_OF_EXPIRY = "Date_of_Expiry"


class PromptTemplates:
    """提示詞模板類別
    
    儲存和管理護照辨識各欄位的提示詞模板。
    """
    
    # 通用提示詞前綴
    COMMON_PREFIX = """這是中華民國（TWN）護照的照片。先從可見欄位讀取；若模糊或被遮擋，改以MRZ兩行（最底部 P<TWN...）做備援。
解析時常見 OCR 錯誤修正：
O↔0、I↔1、B↔8、S↔5、G↔6、Z↔2、< 代表空白或連字號、<< 代表逗號或姓/名分隔。
僅輸出指定欄位；不得輸出多餘個資。無法判定時回傳 null 並附 reason。
日期輸出一律 YYYY-MM-DD；月份英文需正確轉換（JAN=01,…,DEC=12）。
回傳 JSON：{"value": "...", "confidence": 0~1, "source": "visual|mrz", "reason": "簡述判斷依據"}

---

"""
    
    # 各欄位的提示詞模板
    TEMPLATES = {
        PassportField.CHINESE_NAME: COMMON_PREFIX + """## 中文名稱（Chinese_Name）
* 目標：擷取護照持有人**中文姓名**（通常位於英文姓名上方或照片左側區塊）。
* 規則：
  1. 優先讀取含有「姓名」或直接以**繁體中文**呈現的姓名字串。
  2. 去除空格、標點與多餘註記（如螢光防偽圖案造成的殘字）。
  3. 若影像區域無法讀取，回傳 `null`。**禁止**用英文姓名或拼音推測中文。
* 輸出：使用上述 JSON 格式。""",
        
        PassportField.ENGLISH_NAME: COMMON_PREFIX + """## 英文名稱（English_Name）
* 目標：擷取**英文姓名**，採「SURNAME, GIVEN NAMES」大寫格式。
* 規則：
  1. 主要來源：`Name (Surname, Given names)` 欄位。
  2. 備援：MRZ 第一行 `P<TWN{SURNAME}<<{GIVEN<NAMES}`：
     * 將 `<<` 轉為 `, `；將單一 `<` 轉為空白或連字號（保留複合名）。
  3. 移除多餘空格；姓氏與名字均大寫。
* 驗證：至少包含一個逗號；姓只含字母與連字號；名可含空白/連字號。
* 輸出：JSON。""",
        
        PassportField.NATIONALITY: COMMON_PREFIX + """## 國籍（Nationality）
* 目標：擷取**國籍**。
* 規則：
  1. 主要來源：`Nationality` 欄位（常見字串：`REPUBLIC OF CHINA`）。
  2. 同時擷取 3 碼國碼（`Code` 或 MRZ 國碼），預期為 `TWN`。
* 輸出：
  ```json
  {"value":{"name":"REPUBLIC OF CHINA","code":"TWN"},"confidence":..., "source":"visual|mrz","reason":"..."}
  ```""",
        
        PassportField.PASSPORT_NUMBER: COMMON_PREFIX + """## 護照號碼（Passport_Number）
* 目標：擷取**護照號碼**。
* 規則：
  1. 主要來源：`Passport No.` 或 `護照號碼` 欄位。
  2. 備援：MRZ 第二行**前 9 位**為號碼，**第 10 位為檢查碼**（不納入號碼）。
  3. 僅允許英數（台灣新版多為 9 碼數字）。移除空白與破折。
* 驗證：
  * 若用 MRZ，請以 ICAO 檢核（加權 7-3-1 循環）驗證第 10 位檢查碼，一致才給高信心。
* 輸出：JSON。""",
        
        PassportField.SEX: COMMON_PREFIX + """## 性別（Sex）
* 目標：擷取**性別**。
* 規則：
  1. 主要來源：`Sex` 欄位，值為 `M`/`F`。
  2. 備援：MRZ 第二行**第 21 位**字元（`M`、`F` 或 `X`）。若為 `X` 視為 `Unspecified`。
* 輸出（例）：`{"value":"F","confidence":..., "source":"visual|mrz","reason":"..."}`""",
        
        PassportField.DATE_OF_BIRTH: COMMON_PREFIX + """## 出生年月日（Date_of_Birth）
* 目標：擷取**出生日期**並轉成 `YYYY-MM-DD`。
* 規則：
  1. 主要來源：`Date of birth` 欄位（格式常為 `DD MON YYYY`）。
  2. 備援：MRZ 第二行**出生日期**為 `YYMMDD`，需轉西元四碼：
     * 年份規則：若 `YY` > 當前年份兩位數，則歸類為 1900s；否則 2000s（可依合理年齡校正）。
  3. 需與性別、效期等欄位的 MRZ 檢查碼一併驗證可得較高信心。
* 輸出：JSON。""",
        
        PassportField.DATE_OF_EXPIRY: COMMON_PREFIX + """## 護照效期（Date_of_Expiry）
* 目標：擷取**護照有效期限（到期日）**並轉成 `YYYY-MM-DD`。
* 規則：
  1. 主要來源：`Date of expiry` 欄位（常為 `DD MON YYYY`）。
  2. 備援：MRZ 第二行**效期** `YYMMDD` → 轉四位年份（同上規則，但效期理應在未來或接近拍攝當年）。
  3. 若影像日期顯示與 MRZ 轉換矛盾，以**能通過 MRZ 檢查碼**的結果為準。
* 輸出：JSON。""",
    }
    
    @classmethod
    def get_prompt(cls, field: PassportField) -> str:
        """取得指定欄位的提示詞
        
        Args:
            field (PassportField): 護照欄位枚舉
        
        Returns:
            str: 該欄位的提示詞模板
        
        Examples:
            >>> prompt = PromptTemplates.get_prompt(PassportField.CHINESE_NAME)
            >>> isinstance(prompt, str)
            True
        
        Raises:
            KeyError: 當欄位不存在於模板中時
        """
        if field not in cls.TEMPLATES:
            raise KeyError(f"提示詞模板中不存在欄位: {field.value}")
        return cls.TEMPLATES[field]
    
    @classmethod
    def get_all_fields(cls) -> list[PassportField]:
        """取得所有可辨識的護照欄位
        
        Returns:
            list[PassportField]: 所有護照欄位的列表
        
        Examples:
            >>> fields = PromptTemplates.get_all_fields()
            >>> len(fields) == 7
            True
        
        Raises:
            此方法不會拋出錯誤
        """
        return list(PassportField)
