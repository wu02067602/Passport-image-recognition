"""
Gemini 影像辨識模組

此模組提供使用 Google Gemini API 進行影像辨識的功能。
"""

from pathlib import Path
from typing import Optional

import google.generativeai as genai


class GeminiImageRecognizer:
    """
    使用 Gemini API 進行影像辨識的類別。
    
    此類別負責：
    1. 讀取圖片檔案
    2. 驗證圖片大小（不超過 15MB）
    3. 將圖片轉換為 base64 格式
    4. 調用 Gemini API 進行影像辨識
    """
    
    MAX_IMAGE_SIZE_MB = 15
    MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        """
        初始化 Gemini 影像辨識器。
        
        Args:
            api_key (Optional[str]): Google Gemini API 金鑰。
                若為 None，則使用 gcloud 認證（需先執行 gcloud auth application-default login）
            model_name (str): 使用的模型名稱，預設為 "gemini-1.5-flash"
        
        Examples:
            >>> # 使用 API 金鑰
            >>> recognizer = GeminiImageRecognizer(api_key="your-api-key")
            
            >>> # 使用 gcloud 認證
            >>> recognizer = GeminiImageRecognizer()
        
        Raises:
            ValueError: 當 api_key 為空字串時（但允許 None）
        """
        if api_key is not None and not api_key:
            raise ValueError("API key 不可為空字串，請傳入有效的金鑰或 None 以使用 gcloud 認證")
        
        # 只有在提供 API key 時才進行配置
        if api_key is not None:
            genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel(model_name)
    
    def _validate_image_size(self, image_path: str) -> None:
        """
        驗證圖片大小是否符合限制。
        
        Args:
            image_path (str): 圖片檔案路徑
        
        Raises:
            FileNotFoundError: 當圖片檔案不存在時
            ValueError: 當圖片大小超過 15MB 時
        """
        path = Path(image_path)
        
        if not path.exists():
            raise FileNotFoundError(f"找不到圖片檔案: {image_path}")
        
        file_size = path.stat().st_size
        if file_size > self.MAX_IMAGE_SIZE_BYTES:
            size_mb = file_size / (1024 * 1024)
            raise ValueError(
                f"圖片大小 {size_mb:.2f}MB 超過限制 {self.MAX_IMAGE_SIZE_MB}MB"
            )
    
    def recognize(self, image_path: str, prompt: str) -> str:
        """
        使用 Gemini API 辨識圖片內容。
        
        Args:
            image_path (str): 圖片檔案路徑
            prompt (str): 給 Gemini 的提示詞
        
        Returns:
            str: Gemini API 回傳的辨識結果
        
        Examples:
            >>> # 使用 API 金鑰
            >>> recognizer = GeminiImageRecognizer(api_key="your-api-key")
            >>> result = recognizer.recognize(
            ...     "/path/to/passport.jpg",
            ...     "請辨識護照號碼"
            ... )
            >>> print(result)
            'A123456789'
            
            >>> # 使用 gcloud 認證
            >>> recognizer = GeminiImageRecognizer()
            >>> result = recognizer.recognize(
            ...     "/path/to/passport.jpg",
            ...     "請辨識護照號碼"
            ... )
            >>> print(result)
            'A123456789'
        
        Raises:
            FileNotFoundError: 當圖片檔案不存在時
            ValueError: 當圖片大小超過 15MB 或 prompt 為空時
            OSError: 當讀取圖片檔案失敗時
            RuntimeError: 當 Gemini API 調用失敗時
        """
        if not prompt:
            raise ValueError("提示詞不可為空")
        
        # 驗證圖片大小
        self._validate_image_size(image_path)
        
        # 讀取圖片
        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
        except OSError as e:
            raise OSError(f"讀取圖片檔案失敗: {e}")
        
        # 調用 Gemini API
        try:
            response = self.model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": image_data}
            ])
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API 調用失敗: {e}")
