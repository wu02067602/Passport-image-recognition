"""圖像理解分析器模組

此模組提供使用 Google Gemini API 進行圖像理解的功能。
"""

import asyncio
from google import genai
from google.genai import types
from typing import Optional
from PIL import Image
from io import BytesIO

from .prompt_templates import PassportField, PromptTemplates


class VisionAnalyzer:
    """圖像理解分析器類別
    
    使用 Google Gemini API 對護照圖片進行文字辨識與理解。
    """
    
    MIME_TYPE_MAP = {
        'JPEG': 'image/jpeg',
        'PNG': 'image/png',
        'WEBP': 'image/webp'
    }
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """初始化圖像理解分析器
        
        使用 gcloud 進行身份驗證，會自動使用 gcloud auth application-default login 的憑證。
        
        Args:
            model_name (str): 使用的模型名稱，預設為 'gemini-2.5-flash'
        
        Examples:
            >>> analyzer = VisionAnalyzer()
            >>> isinstance(analyzer, VisionAnalyzer)
            True
        
        Raises:
            ValueError: 當模型名稱為空時
            RuntimeError: 當 gcloud 認證失敗時
        """
        if not model_name:
            raise ValueError("模型名稱不可為空")
        
        try:
            self.client = genai.Client(vertexai=True)
            self.model_name = model_name
        except (ValueError, TypeError) as e:
            raise RuntimeError(f"初始化 Gemini 模型失敗，請確認已執行 gcloud auth application-default login: {str(e)}") from e
    
    def _get_image_mime_type(self, img_bytes: bytes) -> str:
        """從圖片位元組資料中偵測 MIME 類型
        
        Args:
            img_bytes (bytes): 圖片的位元組資料
        
        Returns:
            str: 圖片的 MIME 類型（例如：'image/jpeg'）
        
        Examples:
            >>> analyzer = VisionAnalyzer()
            >>> with open("test.jpg", "rb") as f:
            ...     img_bytes = f.read()
            >>> mime_type = analyzer._get_image_mime_type(img_bytes)
            >>> mime_type in ['image/jpeg', 'image/png', 'image/webp']
            True
        
        Raises:
            ValueError: 當無法辨識圖片格式或格式不支援時
        """
        try:
            with Image.open(BytesIO(img_bytes)) as image:
                if image.format not in self.MIME_TYPE_MAP:
                    supported_formats = ', '.join(self.MIME_TYPE_MAP.keys())
                    raise ValueError(
                        f"不支援的圖片格式: {image.format}。"
                        f"支援的格式: {supported_formats}"
                    )
                return self.MIME_TYPE_MAP[image.format]
        except OSError as e:
            raise ValueError(f"無法辨識圖片格式") from e
    
    def analyze_field_from_bytes(
        self,
        img_bytes: bytes,
        field: PassportField,
        custom_prompt: Optional[str] = None
    ) -> str:
        """從圖片位元組資料分析護照圖片中的特定欄位
        
        Args:
            img_bytes (bytes): 護照圖片的位元組資料
            field (PassportField): 要分析的護照欄位
            custom_prompt (Optional[str]): 自訂提示詞，若未提供則使用預設模板
        
        Returns:
            str: LLM 返回的 JSON 字串結果
        
        Examples:
            >>> analyzer = VisionAnalyzer()
            >>> with open("passport.jpg", "rb") as f:
            ...     img_bytes = f.read()
            >>> result = analyzer.analyze_field_from_bytes(img_bytes, PassportField.CHINESE_NAME)
            >>> isinstance(result, str)
            True
        
        Raises:
            ValueError: 當圖片格式不支援或無法辨識時
            RuntimeError: 當 API 呼叫失敗時
        """
        prompt = custom_prompt if custom_prompt else PromptTemplates.get_prompt(field)
        
        # 偵測圖片格式（驗證錯誤應直接向上傳播，不應被 API 錯誤處理器捕捉）
        mime_type = self._get_image_mime_type(img_bytes)
        
        # 建立文字與影像的 Part（這些操作可能產生 API 參數錯誤）
        try:
            prompt_part = types.Part.from_text(text=prompt)
            image_part = types.Part.from_bytes(data=img_bytes, mime_type=mime_type)

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt_part, image_part]
            )
            return response.text
        except (ValueError, TypeError) as e:
            raise RuntimeError(f"Gemini API 呼叫參數錯誤: {str(e)}") from e
        except ConnectionError as e:
            raise RuntimeError(f"Gemini API 連線失敗: {str(e)}") from e
    
    async def analyze_all_fields_from_bytes(
        self,
        img_bytes: bytes
    ) -> dict[PassportField, str]:
        """從圖片位元組資料分析護照圖片中的所有欄位
        
        使用非同步方式並發執行所有欄位的 LLM 分析。
        
        Args:
            img_bytes (bytes): 護照圖片的位元組資料
        
        Returns:
            dict[PassportField, str]: 每個欄位對應的 LLM 回應結果
        
        Examples:
            >>> import asyncio
            >>> analyzer = VisionAnalyzer()
            >>> with open("passport.jpg", "rb") as f:
            ...     img_bytes = f.read()
            >>> results = asyncio.run(analyzer.analyze_all_fields_from_bytes(img_bytes))
            >>> isinstance(results, dict)
            True
            >>> PassportField.CHINESE_NAME in results
            True
        
        Raises:
            ValueError: 當圖片格式不支援或無法辨識時
            RuntimeError: 當任一 API 呼叫失敗時
        """
        all_fields = PromptTemplates.get_all_fields()
        
        # 使用 asyncio.to_thread() 將同步的 API 呼叫包裝為非同步任務
        # 使用 asyncio.gather() 並發執行所有欄位的分析
        tasks = [
            asyncio.to_thread(self.analyze_field_from_bytes, img_bytes, field)
            for field in all_fields
        ]
        
        # 並發執行所有任務，並收集結果
        results_list = await asyncio.gather(*tasks, return_exceptions=False)
        
        # 將結果列表轉換為字典
        results = {
            field: result
            for field, result in zip(all_fields, results_list)
        }
        
        return results
