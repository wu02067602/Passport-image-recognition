"""圖像理解分析器模組

此模組提供使用 Google Gemini API 進行圖像理解的功能。
"""

import asyncio
import logging
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from google import genai
from google.genai import types
from typing import Optional
from PIL import Image
from io import BytesIO

from .prompt_templates import PassportField, PromptTemplates


# Gemini API 同時呼叫數上限（控制 thread pool 大小）
# 建議範圍：32~48，可依實測調整
GEMINI_MAX_WORKERS = int(os.environ.get('GEMINI_MAX_WORKERS', '50'))

# 設定 logger
logger = logging.getLogger(__name__)


class VisionAnalyzer:
    """圖像理解分析器類別
    
    使用 Google Gemini API 對護照圖片進行文字辨識與理解。
    """
    
    MIME_TYPE_MAP = {
        'JPEG': 'image/jpeg',
        'PNG': 'image/png',
        'WEBP': 'image/webp'
    }
    
    # 類別層級的專用 ThreadPoolExecutor，用於控制 Gemini API 同時呼叫數
    _executor: ThreadPoolExecutor | None = None
    # 用於保護 executor 初始化的鎖
    _executor_lock = threading.Lock()
    
    @classmethod
    def get_executor(cls) -> ThreadPoolExecutor:
        """取得專用的 ThreadPoolExecutor
        
        使用執行緒安全的延遲初始化，確保只建立一個 executor 實例。
        採用雙重檢查鎖定模式（Double-Checked Locking）以兼顧效能與執行緒安全。
        
        Returns:
            ThreadPoolExecutor: 專用的 thread pool executor
        
        Examples:
            >>> executor = VisionAnalyzer.get_executor()
            >>> isinstance(executor, ThreadPoolExecutor)
            True
        
        Raises:
            此函數不會拋出錯誤
        """
        # 雙重檢查鎖定模式（Double-Checked Locking）
        # 第一次檢查：避免不必要的鎖定開銷（當 executor 已存在時）
        if cls._executor is None:
            with cls._executor_lock:
                # 第二次檢查：確保只有一個執行緒能建立 executor
                if cls._executor is None:
                    cls._executor = ThreadPoolExecutor(max_workers=GEMINI_MAX_WORKERS)
                    logger.info(f"建立 Gemini ThreadPoolExecutor: max_workers={GEMINI_MAX_WORKERS}")
        return cls._executor
    
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
    
    def _analyze_field_with_image_part(
        self,
        image_part: types.Part,
        field: PassportField,
        custom_prompt: Optional[str] = None
    ) -> tuple[str, float]:
        """使用預先建立的 image_part 分析護照圖片中的特定欄位
        
        此方法避免每個欄位重複建立 image_part，提升效能。
        
        Args:
            image_part (types.Part): 預先建立的圖片 Part 物件
            field (PassportField): 要分析的護照欄位
            custom_prompt (Optional[str]): 自訂提示詞，若未提供則使用預設模板
        
        Returns:
            tuple[str, float]: (LLM 返回的 JSON 字串結果, 此欄位的 API 呼叫耗時秒數)
        
        Examples:
            >>> analyzer = VisionAnalyzer()
            >>> with open("passport.jpg", "rb") as f:
            ...     img_bytes = f.read()
            >>> image_part = types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg')
            >>> result, elapsed = analyzer._analyze_field_with_image_part(image_part, PassportField.CHINESE_NAME)
            >>> isinstance(result, str)
            True
        
        Raises:
            RuntimeError: 當 API 呼叫失敗時
        """
        prompt = custom_prompt if custom_prompt else PromptTemplates.get_prompt(field)
        start_time = time.perf_counter()
        
        try:
            prompt_part = types.Part.from_text(text=prompt)

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt_part, image_part]
            )
            elapsed = time.perf_counter() - start_time
            return response.text, elapsed
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
        採用專用 ThreadPoolExecutor 控制同時呼叫數，並重用 image_part 避免重複 PIL 開圖。
        
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
        start_time = time.perf_counter()
        
        # 只做一次 MIME 類型偵測（避免每欄位重複 PIL open）
        mime_type = self._get_image_mime_type(img_bytes)
        
        # 只建立一次 image_part（7 個欄位呼叫共用同一份）
        image_part = types.Part.from_bytes(data=img_bytes, mime_type=mime_type)
        
        mime_elapsed = time.perf_counter() - start_time
        logger.debug(f"MIME 偵測與 image_part 建立完成: 耗時={mime_elapsed:.4f}s")
        
        all_fields = PromptTemplates.get_all_fields()
        loop = asyncio.get_running_loop()
        executor = self.get_executor()
        
        # 使用專用 ThreadPoolExecutor 的 run_in_executor
        # 取代 asyncio.to_thread()，讓同時 Gemini 呼叫數可控
        tasks = [
            loop.run_in_executor(
                executor,
                self._analyze_field_with_image_part,
                image_part,
                field,
                None  # custom_prompt
            )
            for field in all_fields
        ]
        
        # 並發執行所有任務，並收集結果
        api_start_time = time.perf_counter()
        results_with_timing = await asyncio.gather(*tasks, return_exceptions=False)
        api_elapsed = time.perf_counter() - api_start_time
        
        # 分離結果與耗時，計算耗時統計
        field_timings: list[float] = []
        results: dict[PassportField, str] = {}
        for field, (result, elapsed) in zip(all_fields, results_with_timing):
            results[field] = result
            field_timings.append(elapsed)
        
        total_elapsed = time.perf_counter() - start_time
        avg_field_time = sum(field_timings) / len(field_timings) if field_timings else 0
        max_field_time = max(field_timings) if field_timings else 0
        min_field_time = min(field_timings) if field_timings else 0
        
        logger.debug(
            f"所有欄位分析完成: 總耗時={total_elapsed:.2f}s, "
            f"欄位數={len(all_fields)}, "
            f"欄位耗時(平均/最大/最小)={avg_field_time:.2f}s/{max_field_time:.2f}s/{min_field_time:.2f}s, "
            f"併發等待耗時={api_elapsed:.2f}s"
        )
        
        return results
