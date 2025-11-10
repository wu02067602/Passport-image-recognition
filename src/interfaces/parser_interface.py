"""
回應解析器介面

定義回應解析器的抽象介面，遵循依賴反轉原則 (DIP)。
"""

from abc import ABC, abstractmethod
from ..parsers.response_parser import PassportInfo


class IResponseParser(ABC):
    """
    回應解析器抽象介面
    
    定義回應解析器必須實作的方法。
    遵循介面隔離原則 (ISP)，只定義必要的方法。
    """
    
    @abstractmethod
    def parse(self, response_text: str) -> PassportInfo:
        """
        解析回應文字
        
        Args:
            response_text (str): 回應文字
            
        Returns:
            PassportInfo: 解析後的護照資訊
        """
        pass
