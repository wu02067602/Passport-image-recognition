"""
護照辨識控制器模組

此模組負責協調影像辨識和結果解析的流程。
遵循單一職責原則 (SRP) 和依賴反轉原則 (DIP)。
"""

from typing import Optional
from ..interfaces.recognizer_interface import IImageRecognizer
from ..interfaces.parser_interface import IResponseParser
from ..parsers.response_parser import ResponseParser, PassportInfo


class PassportRecognitionController:
    """
    護照辨識控制器
    
    負責協調影像辨識器和回應解析器，完成護照資訊的識別和解析流程。
    使用依賴注入 (Dependency Injection) 遵循依賴反轉原則 (DIP)。
    依賴抽象介面而非具體實作，提高彈性和可測試性。
    
    Attributes:
        recognizer (IImageRecognizer): 影像辨識器實例
        parser (IResponseParser): 回應解析器實例
    """
    
    # 預設的提示詞範本，設計為 JSON 格式輸出，便於解析
    DEFAULT_PROMPT_TEMPLATE = """請辨識此護照圖片中的以下資訊，並以 JSON 格式回傳：

{
  "passport_number": "護照號碼",
  "gender": "性別 (男/女)",
  "birth_date": "生日 (YYYY-MM-DD 格式)",
  "chinese_name": "中文姓名",
  "english_name": "英文姓名"
}

注意事項：
1. 如果某個欄位無法辨識，請填入 null
2. 生日請使用 YYYY-MM-DD 格式（例如：1990-01-01）
3. 性別請使用「男」或「女」
4. 護照號碼通常是一組英文字母和數字的組合
5. 請確保回傳的是有效的 JSON 格式

請辨識護照上的資訊："""
    
    def __init__(
        self,
        recognizer: IImageRecognizer,
        parser: Optional[IResponseParser] = None
    ):
        """
        初始化控制器
        
        Args:
            recognizer (IImageRecognizer): 影像辨識器實例（依賴抽象介面）
            parser (Optional[IResponseParser]): 回應解析器實例，若未提供則使用預設解析器（依賴抽象介面）
        """
        self.recognizer = recognizer
        self.parser = parser if parser is not None else ResponseParser()
    
    def recognize_passport(
        self,
        image_path: str,
        custom_prompt: Optional[str] = None
    ) -> PassportInfo:
        """
        辨識護照資訊
        
        此方法會：
        1. 使用影像辨識器處理圖片
        2. 使用解析器解析 LLM 回應
        3. 返回結構化的護照資訊
        
        Args:
            image_path (str): 護照圖片的檔案路徑
            custom_prompt (Optional[str]): 自訂提示詞，若未提供則使用預設提示詞
            
        Returns:
            PassportInfo: 解析後的護照資訊物件
            
        Raises:
            ImageNotFoundError: 當圖片檔案不存在時
            ImageSizeError: 當圖片大小超過限制時
        """
        # 使用自訂提示詞或預設提示詞
        prompt = custom_prompt if custom_prompt else self.DEFAULT_PROMPT_TEMPLATE
        
        # 執行影像辨識
        raw_response = self.recognizer.recognize(image_path, prompt)
        
        # 解析回應
        passport_info = self.parser.parse(raw_response)
        
        return passport_info
    
    def recognize_passport_raw(
        self,
        image_path: str,
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        辨識護照資訊並返回原始回應
        
        此方法只執行影像辨識，不進行解析，適合需要原始 LLM 回應的情境。
        
        Args:
            image_path (str): 護照圖片的檔案路徑
            custom_prompt (Optional[str]): 自訂提示詞，若未提供則使用預設提示詞
            
        Returns:
            str: LLM 的原始回應文字
            
        Raises:
            ImageNotFoundError: 當圖片檔案不存在時
            ImageSizeError: 當圖片大小超過限制時
        """
        # 使用自訂提示詞或預設提示詞
        prompt = custom_prompt if custom_prompt else self.DEFAULT_PROMPT_TEMPLATE
        
        # 執行影像辨識
        raw_response = self.recognizer.recognize(image_path, prompt)
        
        return raw_response
    
    @staticmethod
    def get_default_prompt() -> str:
        """
        取得預設提示詞
        
        Returns:
            str: 預設提示詞內容
        """
        return PassportRecognitionController.DEFAULT_PROMPT_TEMPLATE
