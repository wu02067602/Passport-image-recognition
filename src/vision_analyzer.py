"""圖像理解分析器模組

此模組提供使用 Google Gemini API 進行圖像理解的功能。
"""

from google import genai
from google.genai import types
from pathlib import Path
from typing import Union, Optional
from PIL import Image

from .prompt_templates import PassportField, PromptTemplates


class VisionAnalyzer:
    """圖像理解分析器類別
    
    使用 Google Gemini API 對護照圖片進行文字辨識與理解。
    """
    
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
    
    def analyze_field(
        self,
        image_path: Union[str, Path],
        field: PassportField,
        custom_prompt: Optional[str] = None
    ) -> str:
        """分析護照圖片中的特定欄位
        
        Args:
            image_path (Union[str, Path]): 護照圖片的路徑
            field (PassportField): 要分析的護照欄位
            custom_prompt (Optional[str]): 自訂提示詞，若未提供則使用預設模板
        
        Returns:
            str: LLM 返回的 JSON 字串結果
        
        Examples:
            >>> analyzer = VisionAnalyzer()
            >>> result = analyzer.analyze_field("passport.jpg", PassportField.CHINESE_NAME)
            >>> isinstance(result, str)
            True
        
        Raises:
            FileNotFoundError: 當圖片檔案不存在時
            ValueError: 當圖片無法開啟時
            RuntimeError: 當 API 呼叫失敗時
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"圖片檔案不存在: {image_path}")
        
        try:
            image = Image.open(image_path)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"圖片檔案不存在: {image_path}") from e
        except OSError as e:
            raise ValueError(f"無法開啟圖片檔案: {image_path}") from e
        
        prompt = custom_prompt if custom_prompt else PromptTemplates.get_prompt(field)
        
        try:
            # 建立文字與影像的 Part（新版 SDK 需以 bytes + mime_type 建立影像 Part）
            prompt_part = types.Part.from_text(text=prompt)

            mime_map = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}
            mime_type = mime_map.get(image.format, "image/jpeg")
            with open(image_path, "rb") as f:
                img_bytes = f.read()
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
    
    def analyze_all_fields(
        self,
        image_path: Union[str, Path]
    ) -> dict[PassportField, str]:
        """分析護照圖片中的所有欄位
        
        對護照的每個欄位逐一呼叫 LLM 進行分析。
        
        Args:
            image_path (Union[str, Path]): 護照圖片的路徑
        
        Returns:
            dict[PassportField, str]: 每個欄位對應的 LLM 回應結果
        
        Examples:
            >>> analyzer = VisionAnalyzer()
            >>> results = analyzer.analyze_all_fields("passport.jpg")
            >>> isinstance(results, dict)
            True
            >>> PassportField.CHINESE_NAME in results
            True
        
        Raises:
            FileNotFoundError: 當圖片檔案不存在時
            ValueError: 當圖片無法開啟時
            RuntimeError: 當任一 API 呼叫失敗時
        """
        results = {}
        all_fields = PromptTemplates.get_all_fields()
        
        for field in all_fields:
            result = self.analyze_field(image_path, field)
            results[field] = result
        
        return results
