"""
回應解析模組

此模組負責解析 LLM 回傳的文字訊息，轉換為結構化的資料格式。
遵循單一職責原則 (SRP)，專注於文字解析功能。
"""

import json
import re
from typing import Dict, Any, Optional
from dataclasses import dataclass
from ..interfaces.parser_interface import IResponseParser


@dataclass
class PassportInfo:
    """
    護照資訊資料類別
    
    Attributes:
        passport_number (str): 護照號碼
        gender (str): 性別
        birth_date (str): 生日
        chinese_name (str): 中文姓名
        english_name (str): 英文姓名
        raw_response (str): 原始回應文字
    """
    passport_number: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    chinese_name: Optional[str] = None
    english_name: Optional[str] = None
    raw_response: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'passport_number': self.passport_number,
            'gender': self.gender,
            'birth_date': self.birth_date,
            'chinese_name': self.chinese_name,
            'english_name': self.english_name,
            'raw_response': self.raw_response
        }


class ResponseParser(IResponseParser):
    """
    回應解析器
    
    實作 IResponseParser 介面，負責將 LLM 回傳的文字訊息解析為結構化的護照資訊。
    支援多種格式：JSON、鍵值對、結構化文字等。
    遵循里氏替換原則 (LSP)，可被其他實作替換。
    """
    
    def __init__(self):
        """初始化解析器"""
        pass
    
    def parse(self, response_text: str) -> PassportInfo:
        """
        解析 LLM 回應文字
        
        嘗試多種解析策略：
        1. JSON 格式解析
        2. 鍵值對格式解析
        3. 結構化文字解析
        
        Args:
            response_text (str): LLM 回傳的文字
            
        Returns:
            PassportInfo: 解析後的護照資訊物件
        """
        # 嘗試 JSON 格式解析
        passport_info = self._try_parse_json(response_text)
        if passport_info:
            passport_info.raw_response = response_text
            return passport_info
        
        # 嘗試鍵值對格式解析
        passport_info = self._try_parse_key_value(response_text)
        if passport_info:
            passport_info.raw_response = response_text
            return passport_info
        
        # 如果都失敗，返回空的護照資訊，但保留原始回應
        return PassportInfo(raw_response=response_text)
    
    def _try_parse_json(self, text: str) -> Optional[PassportInfo]:
        """
        嘗試以 JSON 格式解析
        
        Args:
            text (str): 回應文字
            
        Returns:
            Optional[PassportInfo]: 解析成功返回 PassportInfo，失敗返回 None
        """
        try:
            # 尋找 JSON 區塊
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                
                return PassportInfo(
                    passport_number=data.get('passport_number') or data.get('護照號碼'),
                    gender=data.get('gender') or data.get('性別'),
                    birth_date=data.get('birth_date') or data.get('生日'),
                    chinese_name=data.get('chinese_name') or data.get('中文姓名'),
                    english_name=data.get('english_name') or data.get('英文姓名')
                )
        except (json.JSONDecodeError, KeyError):
            pass
        
        return None
    
    def _try_parse_key_value(self, text: str) -> Optional[PassportInfo]:
        """
        嘗試以鍵值對格式解析
        
        支援格式範例：
        - 護照號碼: 123456789
        - 性別: 男
        - passport_number: 123456789
        - gender: Male
        
        Args:
            text (str): 回應文字
            
        Returns:
            Optional[PassportInfo]: 解析成功返回 PassportInfo，失敗返回 None
        """
        # 定義欄位對應
        field_patterns = {
            'passport_number': [
                r'護照號碼[:：]\s*([^\n]+)',
                r'passport[_\s]number[:：]\s*([^\n]+)',
                r'passport[:：]\s*([^\n]+)'
            ],
            'gender': [
                r'性別[:：]\s*([^\n]+)',
                r'gender[:：]\s*([^\n]+)'
            ],
            'birth_date': [
                r'生日[:：]\s*([^\n]+)',
                r'出生日期[:：]\s*([^\n]+)',
                r'birth[_\s]date[:：]\s*([^\n]+)',
                r'date[_\s]of[_\s]birth[:：]\s*([^\n]+)'
            ],
            'chinese_name': [
                r'中文姓名[:：]\s*([^\n]+)',
                r'中文名字[:：]\s*([^\n]+)',
                r'chinese[_\s]name[:：]\s*([^\n]+)'
            ],
            'english_name': [
                r'英文姓名[:：]\s*([^\n]+)',
                r'英文名字[:：]\s*([^\n]+)',
                r'english[_\s]name[:：]\s*([^\n]+)'
            ]
        }
        
        result = {}
        found_any = False
        
        for field, patterns in field_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    result[field] = match.group(1).strip()
                    found_any = True
                    break
        
        if found_any:
            return PassportInfo(
                passport_number=result.get('passport_number'),
                gender=result.get('gender'),
                birth_date=result.get('birth_date'),
                chinese_name=result.get('chinese_name'),
                english_name=result.get('english_name')
            )
        
        return None
