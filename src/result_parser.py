"""結果解析器模組

此模組提供解析 LLM 回應結果的功能。
"""

import json
import re
from typing import Any
from .prompt_templates import PassportField


class ParseError(Exception):
    """解析錯誤異常類別"""
    pass


class ResultParser:
    """結果解析器類別
    
    負責將 LLM 返回的 JSON 字串解析成結構化的護照資料。
    """
    
    def parse_llm_response(self, response: str) -> dict[str, Any]:
        """解析 LLM 回應的 JSON 字串
        
        Args:
            response (str): LLM 返回的回應字串
        
        Returns:
            dict[str, Any]: 解析後的字典，包含 value、confidence、source、reason 等欄位
        
        Examples:
            >>> parser = ResultParser()
            >>> response = '{"value": "張三", "confidence": 0.95, "source": "visual", "reason": "清晰可見"}'
            >>> result = parser.parse_llm_response(response)
            >>> result['value']
            '張三'
        
        Raises:
            ParseError: 當 JSON 解析失敗或格式不正確時
        """
        # 移除可能的 markdown code block 標記
        cleaned_response = self._clean_response(response)
        
        try:
            parsed_data = json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            raise ParseError(f"JSON 解析失敗: {str(e)}") from e
        
        # 驗證必要欄位
        if not isinstance(parsed_data, dict):
            raise ParseError("回應格式錯誤：預期為 JSON 物件")
        
        return parsed_data
    
    def _clean_response(self, response: str) -> str:
        """清理回應字串，移除 markdown 標記
        
        Args:
            response (str): 原始回應字串
        
        Returns:
            str: 清理後的 JSON 字串
        
        Examples:
            >>> parser = ResultParser()
            >>> parser._clean_response('```json\\n{"value": "test"}\\n```')
            '{"value": "test"}'
        
        Raises:
            此方法不會拋出錯誤
        """
        # 移除 markdown code block
        response = re.sub(r'^```json\s*\n', '', response, flags=re.MULTILINE)
        response = re.sub(r'^```\s*\n', '', response, flags=re.MULTILINE)
        response = re.sub(r'\n```$', '', response, flags=re.MULTILINE)
        return response.strip()
    
    def parse_all_fields(
        self,
        raw_results: dict[PassportField, str]
    ) -> dict[str, Any]:
        """解析所有欄位的 LLM 回應
        
        將每個護照欄位的 LLM 回應解析成結構化資料，並組合成標準格式。
        如果資料格式錯誤（如中文名含英文），該欄位的值會變成 None，
        並將錯誤資訊放入 validation_errors 欄位。
        
        Args:
            raw_results (dict[PassportField, str]): 各欄位的原始 LLM 回應
        
        Returns:
            dict[str, Any]: 包含所有護照資訊的字典，包含以下欄位：
                - 中文名稱 (Optional[str])
                - 英文名稱 (str)
                - 國籍 (dict with 'name' and 'code')
                - 護照號碼 (str)
                - 性別 (str)
                - 出生年月日 (str, format: YYYY-MM-DD)
                - 護照效期 (str, format: YYYY-MM-DD)
                - validation_errors (Optional[dict]): 驗證錯誤訊息集合
        
        Examples:
            >>> parser = ResultParser()
            >>> raw_results = {
            ...     PassportField.CHINESE_NAME: '{"value": "張三", "confidence": 0.95, "source": "visual", "reason": "清晰"}',
            ...     PassportField.ENGLISH_NAME: '{"value": "CHANG, SAN", "confidence": 0.98, "source": "visual", "reason": "清晰"}'
            ... }
            >>> result = parser.parse_all_fields(raw_results)
            >>> '中文名稱' in result
            True
        
        Raises:
            ParseError: 當任一欄位解析失敗時
        """
        passport_data = {
            '中文名稱': None,
            '英文名稱': None,
            '國籍': None,
            '護照號碼': None,
            '性別': None,
            '出生年月日': None,
            '護照效期': None,
        }
        
        validation_errors = {}
        
        field_mapping = {
            PassportField.CHINESE_NAME: '中文名稱',
            PassportField.ENGLISH_NAME: '英文名稱',
            PassportField.NATIONALITY: '國籍',
            PassportField.PASSPORT_NUMBER: '護照號碼',
            PassportField.SEX: '性別',
            PassportField.DATE_OF_BIRTH: '出生年月日',
            PassportField.DATE_OF_EXPIRY: '護照效期',
        }
        
        for field, raw_response in raw_results.items():
            chinese_field_name = field_mapping.get(field)
            if not chinese_field_name:
                continue
                
            try:
                parsed = self.parse_llm_response(raw_response)
                value = parsed.get('value')
                
                # 資料驗證邏輯
                error_msg = None
                if value is not None:
                    # 定義欄位與驗證函數的對應關係
                    validators = {
                        PassportField.CHINESE_NAME: self._validate_chinese_name,
                        PassportField.ENGLISH_NAME: self._validate_english_name,
                        PassportField.PASSPORT_NUMBER: self._validate_passport_number,
                        PassportField.DATE_OF_BIRTH: self._validate_date,
                        PassportField.DATE_OF_EXPIRY: self._validate_date,
                    }
                    
                    validator = validators.get(field)
                    if validator:
                        error_msg = validator(value)
                
                if error_msg:
                    # 驗證失敗：設為 None 並記錄錯誤
                    passport_data[chinese_field_name] = None
                    validation_errors[chinese_field_name] = error_msg
                else:
                    # 驗證成功或無需驗證
                    if value is not None:
                        passport_data[chinese_field_name] = value
                        
            except ParseError as e:
                # 解析失敗時記錄錯誤但繼續處理其他欄位
                passport_data[chinese_field_name] = None
                validation_errors[chinese_field_name] = f"解析錯誤: {str(e)}"
        
        # 如果有驗證錯誤，將其加入結果中
        if validation_errors:
            passport_data['validation_errors'] = validation_errors
            
        return passport_data

    def _validate_chinese_name(self, name: str) -> str | None:
        """驗證中文名稱
        
        規則：不能包含英文字母 (a-z, A-Z)
        """
        if not isinstance(name, str):
            return "格式錯誤：必須為字串"
            
        if re.search(r'[a-zA-Z]', name):
            return "格式錯誤：中文名稱不可包含英文字母"
        return None

    def _validate_english_name(self, name: str) -> str | None:
        """驗證英文名稱
        
        規則：
        1. 不能包含中文字元 (\u4e00-\u9fff)
        2. 長度不能超過 35 個字元
        """
        if not isinstance(name, str):
            return "格式錯誤：必須為字串"
            
        if len(name) > 35:
            return f"格式錯誤：英文名稱長度過長（目前 {len(name)} 字元，上限 35 字元）"
            
        if re.search(r'[\u4e00-\u9fff]', name):
            return "格式錯誤：英文名稱不可包含中文字元"
        return None

    def _validate_passport_number(self, number: str) -> str | None:
        """驗證護照號碼
        
        規則：必須為 9 碼數字。
        """
        if not isinstance(number, str):
            return "格式錯誤：必須為字串"
            
        number = number.strip().upper()
        
        if len(number) != 9:
            return f"格式錯誤：護照號碼長度應為 9 碼，目前為 {len(number)} 碼"
            
        # 檢查是否全為數字
        if not number.isdigit():
            return "格式錯誤：護照號碼必須全為數字"
            
        return None
        
    def _validate_date(self, date_str: str) -> str | None:
        """驗證日期格式
        
        規則：必須為 YYYY-MM-DD 格式 (確保不含非數字字符)
        """
        if not isinstance(date_str, str):
            return "格式錯誤：必須為字串"
            
        # 檢查基本格式 YYYY-MM-DD (這已經隱含排除英文字母，因為 \d 只匹配數字)
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return "格式錯誤：日期必須為 YYYY-MM-DD 格式且不含英文字母"
            
        return None
