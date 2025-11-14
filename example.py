"""使用範例

此檔案展示如何透過 BASE64 API 執行護照辨識。
"""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Final

from src import PassportService

SUPPORTED_FORMATS: Final[set[str]] = {'.jpg', '.jpeg', '.png', '.webp'}


def encode_image_to_base64(image_path: Path) -> str:
    """
    將圖片檔案轉換為 BASE64 字串。
    
    Args:
        image_path (Path): 護照圖片檔案的路徑
    
    Returns:
        str: BASE64 編碼後的圖片字串
    
    Examples:
        >>> encode_image_to_base64(Path("passport.jpg"))  # doctest: +SKIP
        'BASE64_STRING'
    
    Raises:
        FileNotFoundError: 當圖片檔案不存在時
        ValueError: 當圖片格式不支援時
        IOError: 當讀取圖片檔案失敗時
    """
    if not image_path.exists():
        raise FileNotFoundError(f"圖片檔案不存在: {image_path}")
    
    if image_path.suffix.lower() not in SUPPORTED_FORMATS:
        supported = ', '.join(sorted(SUPPORTED_FORMATS))
        raise ValueError(f"不支援的圖片格式: {image_path.suffix}，支援: {supported}")
    
    try:
        image_bytes = image_path.read_bytes()
    except OSError as exc:
        raise IOError(f"讀取圖片檔案失敗: {image_path}") from exc
    
    return base64.b64encode(image_bytes).decode('utf-8')


def main() -> None:
    """
    透過 PassportService 執行 BASE64 護照辨識的示範。
    
    Args:
        None
    
    Returns:
        None
    
    Examples:
        >>> main()  # doctest: +SKIP
    
    Raises:
        此函數不會拋出錯誤，所有錯誤都會被捕捉並輸出。
    """
    service = PassportService()
    passport_image_path = Path("path/to/passport.jpg")
    
    try:
        base64_image = encode_image_to_base64(passport_image_path)
        result = service.recognize_from_base64(base64_image)
        
        print("=== 護照辨識結果 ===")
        print(f"中文名稱: {result.get('中文名稱')}")
        print(f"英文名稱: {result.get('英文名稱')}")
        print(f"國籍: {result.get('國籍')}")
        print(f"護照號碼: {result.get('護照號碼')}")
        print(f"性別: {result.get('性別')}")
        print(f"出生年月日: {result.get('出生年月日')}")
        print(f"護照效期: {result.get('護照效期')}")
        
    except (FileNotFoundError, ValueError, IOError, RuntimeError) as exc:
        print(f"錯誤：{exc}")


if __name__ == "__main__":
    main()
