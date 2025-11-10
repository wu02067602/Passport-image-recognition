"""
影像辨識模組

此模組負責處理圖片讀取、驗證及使用 Gemini API 進行影像辨識。
遵循單一職責原則 (SRP)，專注於影像辨識的核心功能。
"""

import base64
import os
from pathlib import Path
from typing import Optional
import google.generativeai as genai
from ..interfaces.recognizer_interface import IImageRecognizer


class ImageSizeError(Exception):
    """圖片大小超過限制時拋出的異常"""
    pass


class ImageNotFoundError(Exception):
    """圖片檔案不存在時拋出的異常"""
    pass


class ImageRecognizer(IImageRecognizer):
    """
    影像辨識類別
    
    實作 IImageRecognizer 介面，負責讀取圖片、驗證圖片大小，並使用 Gemini API 進行影像辨識。
    遵循里氏替換原則 (LSP)，可被其他實作替換。
    
    Attributes:
        max_size_mb (int): 圖片大小上限（MB），預設為 15MB
        api_key (str): Gemini API 金鑰
    """
    
    MAX_FILE_SIZE_MB = 15
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    
    def __init__(self, api_key: str):
        """
        初始化影像辨識器
        
        Args:
            api_key (str): Gemini API 金鑰
        """
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def validate_image_path(self, image_path: str) -> Path:
        """
        驗證圖片路徑是否存在
        
        Args:
            image_path (str): 圖片檔案路徑
            
        Returns:
            Path: 驗證後的 Path 物件
            
        Raises:
            ImageNotFoundError: 當圖片檔案不存在時
        """
        path = Path(image_path)
        if not path.exists():
            raise ImageNotFoundError(f"圖片檔案不存在: {image_path}")
        if not path.is_file():
            raise ImageNotFoundError(f"路徑不是檔案: {image_path}")
        return path
    
    def validate_image_size(self, image_path: Path) -> None:
        """
        驗證圖片大小是否符合限制
        
        Args:
            image_path (Path): 圖片檔案路徑
            
        Raises:
            ImageSizeError: 當圖片大小超過 15MB 時
        """
        file_size = image_path.stat().st_size
        if file_size > self.MAX_FILE_SIZE_BYTES:
            size_mb = file_size / (1024 * 1024)
            raise ImageSizeError(
                f"圖片大小 {size_mb:.2f}MB 超過限制 {self.MAX_FILE_SIZE_MB}MB"
            )
    
    def read_image_as_base64(self, image_path: Path) -> str:
        """
        讀取圖片並轉換為 base64 格式
        
        Args:
            image_path (Path): 圖片檔案路徑
            
        Returns:
            str: base64 編碼的圖片字串
        """
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
        return base64_image
    
    def recognize(self, image_path: str, prompt: str) -> str:
        """
        執行影像辨識
        
        此方法會：
        1. 驗證圖片路徑
        2. 驗證圖片大小
        3. 讀取圖片
        4. 呼叫 Gemini API 進行辨識
        
        Args:
            image_path (str): 圖片檔案路徑
            prompt (str): 提示詞，用於指導 LLM 辨識內容
            
        Returns:
            str: LLM 回傳的辨識結果文字
            
        Raises:
            ImageNotFoundError: 當圖片檔案不存在時
            ImageSizeError: 當圖片大小超過限制時
        """
        # 驗證圖片路徑
        path = self.validate_image_path(image_path)
        
        # 驗證圖片大小
        self.validate_image_size(path)
        
        # 讀取圖片
        with open(path, 'rb') as image_file:
            image_data = image_file.read()
        
        # 呼叫 Gemini API
        response = self.model.generate_content([
            prompt,
            {"mime_type": self._get_mime_type(path), "data": image_data}
        ])
        
        return response.text
    
    def _get_mime_type(self, image_path: Path) -> str:
        """
        根據副檔名取得 MIME type
        
        Args:
            image_path (Path): 圖片檔案路徑
            
        Returns:
            str: MIME type
        """
        extension = image_path.suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp'
        }
        return mime_types.get(extension, 'image/jpeg')
