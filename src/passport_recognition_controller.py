"""
護照辨識控制器模組

此模組提供護照辨識的控制邏輯。
"""

from typing import Dict, Optional

from src.gemini_image_recognizer import GeminiImageRecognizer
from src.response_parser import ResponseParser, PassportRecognitionResult


class PassportRecognitionController:
    """
    護照辨識控制器類別。
    
    此類別負責：
    1. 管理辨識流程
    2. 設計格式化的提示詞
    3. 調用 GeminiImageRecognizer 進行辨識
    """
    
    DEFAULT_PROMPT_TEMPLATE = """請仔細辨識此護照圖片中的資訊。

請以 JSON 格式回傳結果，格式如下：
{{
    "passport_number": "護照號碼",
    "confidence": "信心度（high/medium/low）"
}}

只需要回傳 JSON 格式的資料，不要包含其他說明文字。
如果無法辨識護照號碼，請將 passport_number 設為 "NOT_FOUND"。
"""
    
    def __init__(
        self,
        recognizer: GeminiImageRecognizer,
        parser: Optional[ResponseParser] = None
    ):
        """
        初始化護照辨識控制器。
        
        Args:
            recognizer (GeminiImageRecognizer): Gemini 影像辨識器實例
            parser (Optional[ResponseParser]): 回應解析器實例，若為 None 則使用預設解析器
        
        Raises:
            TypeError: 當 recognizer 不是 GeminiImageRecognizer 實例時
        """
        if not isinstance(recognizer, GeminiImageRecognizer):
            raise TypeError("recognizer 必須是 GeminiImageRecognizer 的實例")
        
        self.recognizer = recognizer
        self.parser = parser if parser else ResponseParser()
    
    def recognize_passport(
        self,
        image_path: str,
        custom_prompt: Optional[str] = None
    ) -> PassportRecognitionResult:
        """
        辨識護照圖片。
        
        Args:
            image_path (str): 護照圖片的檔案路徑
            custom_prompt (Optional[str]): 自訂提示詞，若為 None 則使用預設提示詞
        
        Returns:
            PassportRecognitionResult: 解析後的護照辨識結果
        
        Examples:
            >>> controller = PassportRecognitionController(recognizer)
            >>> result = controller.recognize_passport("/path/to/passport.jpg")
            >>> print(result.passport_number)
            'A123456789'
            >>> print(result.confidence)
            'high'
        
        Raises:
            ValueError: 當 image_path 為空字串時
            FileNotFoundError: 當圖片檔案不存在時
            ValueError: 當圖片大小超過 15MB 時
            OSError: 當讀取圖片檔案失敗時
            RuntimeError: 當 Gemini API 調用失敗時
            ValueError: 當無法解析回應內容時
        """
        if not image_path:
            raise ValueError("圖片路徑不可為空")
        
        # 使用自訂提示詞或預設提示詞
        prompt = custom_prompt if custom_prompt else self.DEFAULT_PROMPT_TEMPLATE
        
        # 調用辨識器進行辨識
        raw_response = self.recognizer.recognize(image_path, prompt)
        
        # 解析辨識結果
        parsed_result = self.parser.parse(raw_response)
        
        return parsed_result
    
    def batch_recognize_passports(
        self,
        image_paths: list[str],
        custom_prompt: Optional[str] = None
    ) -> Dict[str, PassportRecognitionResult]:
        """
        批次辨識多張護照圖片。
        
        Args:
            image_paths (list[str]): 護照圖片的檔案路徑列表
            custom_prompt (Optional[str]): 自訂提示詞，若為 None 則使用預設提示詞
        
        Returns:
            Dict[str, PassportRecognitionResult]: 以圖片路徑為鍵，
                解析後的辨識結果為值的字典
        
        Examples:
            >>> controller = PassportRecognitionController(recognizer)
            >>> paths = ["/path/to/passport1.jpg", "/path/to/passport2.jpg"]
            >>> results = controller.batch_recognize_passports(paths)
            >>> for path, result in results.items():
            ...     print(f"{path}: {result.passport_number}")
            /path/to/passport1.jpg: A123456789
            /path/to/passport2.jpg: B987654321
        
        Raises:
            ValueError: 當 image_paths 為空列表時
        """
        if not image_paths:
            raise ValueError("圖片路徑列表不可為空")
        
        results = {}
        for image_path in image_paths:
            try:
                result = self.recognize_passport(image_path, custom_prompt)
                results[image_path] = result
            except (FileNotFoundError, ValueError, OSError, RuntimeError) as e:
                # 處理錯誤，建立一個表示錯誤的結果物件
                results[image_path] = PassportRecognitionResult(
                    passport_number="ERROR",
                    confidence="unknown",
                    raw_response=f"ERROR: {str(e)}"
                )
        
        return results
