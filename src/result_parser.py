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
            try:
                parsed = self.parse_llm_response(raw_response)
                chinese_field_name = field_mapping.get(field)
                
                if chinese_field_name:
                    # 提取 value 欄位
                    value = parsed.get('value')
                    if value is not None:
                        passport_data[chinese_field_name] = value
            except ParseError as e:
                # 解析失敗時記錄錯誤但繼續處理其他欄位
                passport_data[field_mapping.get(field, field.value)] = {
                    'error': str(e),
                    'raw_response': raw_response
                }
        
        return passport_data
    
