"""護照控制器模組

此模組提供護照辨識的主控制器，協調所有模組的交互。
"""

from pathlib import Path
from typing import Union, Any, Optional

from .image_encoder import ImageEncoder
from .vision_analyzer import VisionAnalyzer
from .result_parser import ResultParser
from .prompt_templates import PassportField


class PassportController:
    """護照辨識控制器類別
    
    負責協調圖片編碼、圖像分析和結果解析等所有模組，
    提供完整的護照辨識流程。
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        """初始化護照辨識控制器
        
        Args:
            api_key (str): Google Gemini API 金鑰
            model_name (str): 使用的模型名稱，預設為 'gemini-1.5-flash'
        
        Examples:
            >>> controller = PassportController(api_key="your_api_key")
            >>> isinstance(controller, PassportController)
            True
        
        Raises:
            ValueError: 當 API 金鑰為空時
        """
        self.image_encoder = ImageEncoder()
        self.vision_analyzer = VisionAnalyzer(api_key=api_key, model_name=model_name)
        self.result_parser = ResultParser()
    
    def recognize_passport(
        self,
        image_path: Union[str, Path]
    ) -> dict[str, Any]:
        """辨識護照圖片中的所有資訊
        
        這是主要的辨識方法，會執行完整的護照辨識流程：
        1. 驗證圖片檔案
        2. 使用 VisionAnalyzer 分析所有欄位
        3. 使用 ResultParser 解析結果
        4. 返回結構化的護照資料
        
        Args:
            image_path (Union[str, Path]): 護照圖片的路徑
        
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
            >>> controller = PassportController(api_key="your_api_key")
            >>> result = controller.recognize_passport("passport.jpg")
            >>> isinstance(result, dict)
            True
            >>> '護照號碼' in result
            True
        
        Raises:
            FileNotFoundError: 當圖片檔案不存在時
            ValueError: 當圖片格式不支援或無法開啟時
            RuntimeError: 當 API 呼叫失敗時
        """
        # 1. 驗證圖片檔案存在且格式正確
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"圖片檔案不存在: {image_path}")
        
        # 驗證圖片格式
        _ = self.image_encoder.get_mime_type(image_path)
        
        # 2. 使用 VisionAnalyzer 分析所有欄位
        raw_results = self.vision_analyzer.analyze_all_fields(image_path)
        
        # 3. 使用 ResultParser 解析結果
        passport_data = self.result_parser.parse_all_fields(raw_results)
        
        return passport_data
    
    def recognize_single_field(
        self,
        image_path: Union[str, Path],
        field: PassportField,
        custom_prompt: Optional[str] = None
    ) -> Any:
        """辨識護照圖片中的單一欄位
        
        Args:
            image_path (Union[str, Path]): 護照圖片的路徑
            field (PassportField): 要辨識的護照欄位
            custom_prompt (Optional[str]): 自訂提示詞，若未提供則使用預設模板
        
        Returns:
            Any: 該欄位的值，若無法辨識則返回 None
        
        Examples:
            >>> controller = PassportController(api_key="your_api_key")
            >>> name = controller.recognize_single_field("passport.jpg", PassportField.CHINESE_NAME)
            >>> isinstance(name, (str, type(None)))
            True
        
        Raises:
            FileNotFoundError: 當圖片檔案不存在時
            ValueError: 當圖片格式不支援或無法開啟時
            RuntimeError: 當 API 呼叫失敗時
        """
        # 1. 驗證圖片檔案
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"圖片檔案不存在: {image_path}")
        
        # 驗證圖片格式
        _ = self.image_encoder.get_mime_type(image_path)
        
        # 2. 使用 VisionAnalyzer 分析指定欄位
        raw_result = self.vision_analyzer.analyze_field(
            image_path,
            field,
            custom_prompt
        )
        
        # 3. 解析結果並提取值
        parsed_result = self.result_parser.parse_llm_response(raw_result)
        value = self.result_parser.extract_value(parsed_result)
        
        return value
    
    def get_supported_formats(self) -> set[str]:
        """取得支援的圖片格式
        
        Returns:
            set[str]: 支援的圖片格式集合（例如: {'.jpg', '.jpeg', '.png'}）
        
        Examples:
            >>> controller = PassportController(api_key="your_api_key")
            >>> formats = controller.get_supported_formats()
            >>> '.jpg' in formats
            True
        
        Raises:
            此方法不會拋出錯誤
        """
        return self.image_encoder.SUPPORTED_FORMATS.copy()
