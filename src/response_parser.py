"""
回應解析器模組

此模組提供解析 LLM 回傳結果的功能。
"""

import json
import re
from typing import Dict, Any, Optional


class PassportRecognitionResult:
    """
    護照辨識結果資料類別。
    
    此類別封裝了護照辨識的結果資料。
    """
    
    def __init__(
        self,
        passport_number: str,
        confidence: str,
        raw_response: Optional[str] = None
    ):
        """
        初始化護照辨識結果。
        
        Args:
            passport_number (str): 護照號碼
            confidence (str): 信心度（high/medium/low）
            raw_response (Optional[str]): 原始 LLM 回應內容
        
        Raises:
            ValueError: 當 passport_number 為空字串時
            ValueError: 當 confidence 不在有效值範圍內時
        """
        if not passport_number:
            raise ValueError("護照號碼不可為空")
        
        valid_confidences = ["high", "medium", "low", "unknown"]
        if confidence not in valid_confidences:
            raise ValueError(
                f"信心度必須為 {valid_confidences} 之一，收到: {confidence}"
            )
        
        self.passport_number = passport_number
        self.confidence = confidence
        self.raw_response = raw_response
    
    def is_found(self) -> bool:
        """
        判斷是否成功辨識護照號碼。
        
        Returns:
            bool: 若成功辨識則為 True，否則為 False
        
        Examples:
            >>> result = PassportRecognitionResult("A123456789", "high")
            >>> result.is_found()
            True
            >>> result = PassportRecognitionResult("NOT_FOUND", "low")
            >>> result.is_found()
            False
        """
        return self.passport_number != "NOT_FOUND"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        將結果轉換為字典格式。
        
        Returns:
            Dict[str, Any]: 包含所有結果資料的字典
        
        Examples:
            >>> result = PassportRecognitionResult("A123456789", "high")
            >>> result.to_dict()
            {
                'passport_number': 'A123456789',
                'confidence': 'high',
                'is_found': True,
                'raw_response': None
            }
        """
        return {
            "passport_number": self.passport_number,
            "confidence": self.confidence,
            "is_found": self.is_found(),
            "raw_response": self.raw_response
        }
    
    def __repr__(self) -> str:
        """字串表示法"""
        return (
            f"PassportRecognitionResult("
            f"passport_number='{self.passport_number}', "
            f"confidence='{self.confidence}')"
        )


class ResponseParser:
    """
    LLM 回應解析器類別。
    
    此類別負責將 LLM 回傳的文字內容解析為結構化的資料。
    """
    
    @staticmethod
    def _extract_json_from_text(text: str) -> str:
        """
        從文字中提取 JSON 內容。
        
        Args:
            text (str): 包含 JSON 的文字內容
        
        Returns:
            str: 提取出的 JSON 字串
        
        Raises:
            ValueError: 當無法找到 JSON 內容時
        """
        # 移除可能的 markdown 程式碼區塊標記
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```\s*", "", text)
        
        # 嘗試找到 JSON 物件
        json_pattern = r'\{[^{}]*\}'
        match = re.search(json_pattern, text, re.DOTALL)
        
        if not match:
            raise ValueError("無法從文字中提取 JSON 內容")
        
        return match.group(0)
    
    @staticmethod
    def parse(response_text: str) -> PassportRecognitionResult:
        """
        解析 LLM 回傳的文字內容。
        
        Args:
            response_text (str): LLM 回傳的文字內容
        
        Returns:
            PassportRecognitionResult: 解析後的護照辨識結果
        
        Examples:
            >>> parser = ResponseParser()
            >>> response = '{"passport_number": "A123456789", "confidence": "high"}'
            >>> result = parser.parse(response)
            >>> result.passport_number
            'A123456789'
            >>> result.confidence
            'high'
        
        Raises:
            ValueError: 當 response_text 為空字串時
            ValueError: 當無法解析 JSON 格式時
            ValueError: 當 JSON 缺少必要欄位時
            ValueError: 當 JSON 欄位值無效時
        """
        if not response_text:
            raise ValueError("回應文字不可為空")
        
        try:
            # 提取 JSON 內容
            json_str = ResponseParser._extract_json_from_text(response_text)
            
            # 解析 JSON
            data = json.loads(json_str)
            
            # 驗證必要欄位
            if "passport_number" not in data:
                raise ValueError("JSON 缺少 'passport_number' 欄位")
            if "confidence" not in data:
                raise ValueError("JSON 缺少 'confidence' 欄位")
            
            # 建立結果物件
            return PassportRecognitionResult(
                passport_number=data["passport_number"],
                confidence=data["confidence"],
                raw_response=response_text
            )
            
        except json.JSONDecodeError as e:
            raise ValueError(f"無效的 JSON 格式: {e}")
        except KeyError as e:
            raise ValueError(f"JSON 缺少必要欄位: {e}")
    
    @staticmethod
    def parse_batch(
        responses: Dict[str, str]
    ) -> Dict[str, PassportRecognitionResult]:
        """
        批次解析多個 LLM 回應。
        
        Args:
            responses (Dict[str, str]): 以圖片路徑為鍵，回應文字為值的字典
        
        Returns:
            Dict[str, PassportRecognitionResult]: 以圖片路徑為鍵，
                解析結果為值的字典
        
        Examples:
            >>> parser = ResponseParser()
            >>> responses = {
            ...     "/path/to/passport1.jpg": '{"passport_number": "A123", ...}',
            ...     "/path/to/passport2.jpg": '{"passport_number": "B456", ...}'
            ... }
            >>> results = parser.parse_batch(responses)
            >>> len(results)
            2
        
        Raises:
            ValueError: 當 responses 為空字典時
        """
        if not responses:
            raise ValueError("回應字典不可為空")
        
        results = {}
        for image_path, response_text in responses.items():
            try:
                results[image_path] = ResponseParser.parse(response_text)
            except ValueError as e:
                # 處理解析失敗的情況，建立一個表示錯誤的結果物件
                results[image_path] = PassportRecognitionResult(
                    passport_number="PARSE_ERROR",
                    confidence="unknown",
                    raw_response=f"ERROR: {str(e)}"
                )
        
        return results
