"""圖片編碼器模組

此模組提供將圖片檔案轉換為 base64 編碼字串的功能。
"""

import base64
from pathlib import Path
from typing import Union


class ImageEncoder:
    """圖片編碼器類別
    
    負責將圖片檔案（JPG 或 PNG）轉換為 base64 編碼的字串。
    """
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png'}
    
    def encode_image(self, image_path: Union[str, Path]) -> str:
        """將圖片檔案轉換為 base64 編碼字串
        
        Args:
            image_path (Union[str, Path]): 圖片檔案的路徑，支援 JPG 或 PNG 格式
        
        Returns:
            str: base64 編碼後的字串
        
        Examples:
            >>> encoder = ImageEncoder()
            >>> base64_str = encoder.encode_image("passport.jpg")
            >>> isinstance(base64_str, str)
            True
        
        Raises:
            FileNotFoundError: 當圖片檔案不存在時
            ValueError: 當圖片格式不支援時（非 JPG 或 PNG）
            IOError: 當讀取圖片檔案失敗時
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"圖片檔案不存在: {image_path}")
        
        if image_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"不支援的圖片格式: {image_path.suffix}。"
                f"支援的格式: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        try:
            with open(image_path, 'rb') as image_file:
                image_bytes = image_file.read()
                encoded_string = base64.b64encode(image_bytes).decode('utf-8')
                return encoded_string
        except IOError as e:
            raise IOError(f"讀取圖片檔案失敗: {image_path}") from e
    
    def get_mime_type(self, image_path: Union[str, Path]) -> str:
        """取得圖片的 MIME 類型
        
        Args:
            image_path (Union[str, Path]): 圖片檔案的路徑
        
        Returns:
            str: 圖片的 MIME 類型（例如: 'image/jpeg', 'image/png'）
        
        Examples:
            >>> encoder = ImageEncoder()
            >>> encoder.get_mime_type("passport.jpg")
            'image/jpeg'
        
        Raises:
            ValueError: 當圖片格式不支援時
        """
        image_path = Path(image_path)
        suffix = image_path.suffix.lower()
        
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png'
        }
        
        if suffix not in mime_types:
            raise ValueError(
                f"不支援的圖片格式: {suffix}。"
                f"支援的格式: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        return mime_types[suffix]
