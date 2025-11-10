"""
影像辨識器介面

定義影像辨識器的抽象介面，遵循依賴反轉原則 (DIP)。
"""

from abc import ABC, abstractmethod


class IImageRecognizer(ABC):
    """
    影像辨識器抽象介面
    
    定義影像辨識器必須實作的方法。
    遵循介面隔離原則 (ISP)，只定義必要的方法。
    """
    
    @abstractmethod
    def recognize(self, image_path: str, prompt: str) -> str:
        """
        執行影像辨識
        
        Args:
            image_path (str): 圖片檔案路徑
            prompt (str): 提示詞
            
        Returns:
            str: 辨識結果文字
        """
        pass
