"""護照辨識服務模組

此模組提供護照辨識服務，支援從 BASE64 編碼的圖片進行辨識。
"""

import base64
from typing import Any

from .vision_analyzer import VisionAnalyzer
from .result_parser import ResultParser


class PassportService:
    """護照辨識服務類別
    
    提供從 BASE64 編碼圖片進行護照辨識的服務。
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """初始化護照辨識服務
        
        Args:
            model_name (str): 使用的模型名稱，預設為 'gemini-2.5-flash'
        
        Examples:
            >>> service = PassportService()
            >>> isinstance(service, PassportService)
            True
        
        Raises:
            ValueError: 當模型名稱為空時
            RuntimeError: 當 gcloud 認證失敗時
        """
        self.vision_analyzer = VisionAnalyzer(model_name=model_name)
        self.result_parser = ResultParser()
    
    async def recognize_from_base64(self, base64_image: str) -> dict[str, Any]:
        """從 BASE64 編碼的圖片辨識護照資訊
        
        使用非同步方式進行辨識，提升執行效率。
        
        Args:
            base64_image (str): BASE64 編碼的圖片字串
        
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
            >>> import asyncio
            >>> service = PassportService()
            >>> with open("passport.jpg", "rb") as f:
            ...     base64_str = base64.b64encode(f.read()).decode('utf-8')
            >>> result = asyncio.run(service.recognize_from_base64(base64_str))
            >>> isinstance(result, dict)
            True
        
        Raises:
            ValueError: 當 BASE64 解碼失敗或圖片格式不支援時
            RuntimeError: 當 API 呼叫失敗時
        """
        # 解碼 BASE64 字串
        try:
            img_bytes = base64.b64decode(base64_image)
        except (ValueError, TypeError) as e:
            raise ValueError(f"BASE64 解碼失敗: {str(e)}") from e
        
        # 使用 VisionAnalyzer 分析所有欄位（非同步並發執行）
        raw_results = await self.vision_analyzer.analyze_all_fields_from_bytes(img_bytes)
        
        # 使用 ResultParser 解析結果
        passport_data = self.result_parser.parse_all_fields(raw_results)
        
        return passport_data
