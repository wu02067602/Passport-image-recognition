"""護照辨識 API 應用程式

此模組提供 Flask API 用於護照辨識，支援單張與批次辨識功能。
"""
import asyncio
import logging
import os
import time

from flask import Flask, request, jsonify
from typing import Any

from src.passport_service import PassportService


# 批次處理每批次最大數量
BATCH_SIZE = 100

# 同時處理的圖片數量上限（控制併發，避免 API 節流）
# 建議範圍：4~6，可依實測調整
IMAGE_CONCURRENCY = int(os.environ.get('IMAGE_CONCURRENCY', '20'))

# 設定 logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


app = Flask(__name__)
passport_service = PassportService()

@app.route('/api/passport/recognize', methods=['POST'])
async def recognize_passport() -> tuple[dict[str, Any], int]:
    """護照辨識 API 端點
    
    接受 BASE64 編碼的圖片，返回護照辨識結果。
    
    Request Body:
        {
            "image": "BASE64 編碼的圖片字串"
        }
    
    Response:
        成功 (200):
        {
            "success": true,
            "data": {
                "中文名稱": "...",
                "英文名稱": "...",
                "國籍": {"name": "...", "code": "..."},
                "護照號碼": "...",
                "性別": "...",
                "出生年月日": "YYYY-MM-DD",
                "護照效期": "YYYY-MM-DD"
            }
        }
        
        失敗 (400/500):
        {
            "success": false,
            "error": "錯誤訊息"
        }
    
    Returns:
        tuple[dict[str, Any], int]: JSON 回應和 HTTP 狀態碼
    
    Examples:
        >>> # 使用 curl 測試
        >>> # curl -X POST http://localhost:8080/api/passport/recognize \
        >>> #   -H "Content-Type: application/json" \
        >>> #   -d '{"image": "BASE64_STRING"}'
    
    Raises:
        此函數不會拋出錯誤，所有錯誤都會被捕捉並返回對應的 HTTP 狀態碼
    """
    try:
        # 驗證請求格式
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': '請求必須為 JSON 格式'
            }), 400
        
        data = request.get_json()
        
        # 驗證必要欄位
        if 'image' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必要欄位: image'
            }), 400
        
        base64_image = data['image']
        request_id = data.get('id')  # 取得 ID，若無則為 None
        
        if not isinstance(base64_image, str) or not base64_image:
            return jsonify({
                'success': False,
                'error': 'image 欄位必須為非空字串'
            }), 400
        
        # 執行護照辨識
        passport_data = await passport_service.recognize_from_base64(base64_image)
        
        return jsonify({
            'success': True,
            'id': request_id,
            'data': passport_data
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'請求參數錯誤: {str(e)}'
        }), 400
    except RuntimeError as e:
        return jsonify({
            'success': False,
            'error': f'辨識服務錯誤: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'未預期的錯誤: {str(e)}'
        }), 500


@app.route('/api/passport/recognize/batch', methods=['POST'])
async def recognize_passport_batch() -> tuple[dict[str, Any], int]:
    """批次護照辨識 API 端點
    
    接受多張圖片資訊（ID 與 BASE64 字串），以非同步方式進行批次辨識。
    每批次處理 100 張圖片，超過則依序分批處理。
    
    Request Body:
        {
            "images": [
                {"id": "FILE_001", "image": "BASE64 編碼的圖片字串"},
                {"id": "FILE_002", "image": "BASE64 編碼的圖片字串"}
            ]
        }
    
    Response:
        成功 (200):
        {
            "success": true,
            "data": {
                "results": [
                    {
                        "id": "FILE_001",
                        "success": true,
                        "data": {
                            "中文名稱": "...",
                            "英文名稱": "...",
                            ...
                        }
                    },
                    ...
                ],
                "total": 10,
                "successful": 8,
                "failed": 2
            }
        }
        失敗 (400/500):
        {
            "success": false,
            "error": "錯誤訊息"
        }
    
    Returns:
        tuple[dict[str, Any], int]: JSON 回應和 HTTP 狀態碼
    
    Examples:
        >>> # 使用 curl 測試
        >>> # curl -X POST http://localhost:8080/api/passport/recognize/batch \
        >>> #   -H "Content-Type: application/json" \
        >>> #   -d '{"images": [{"id": "FILE_001", "image": "BASE64_STRING_1"}, {"id": "FILE_002", "image": "BASE64_STRING_2"}]}'
    
    Raises:
        此函數不會拋出錯誤，所有錯誤都會被捕捉並返回對應的 HTTP 狀態碼
    """
    try:
        # 驗證請求格式
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': '請求必須為 JSON 格式'
            }), 400
        
        data = request.get_json()
        
        # 驗證必要欄位
        if 'images' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必要欄位: images'
            }), 400
        
        images = data['images']
        
        if not isinstance(images, list):
            return jsonify({
                'success': False,
                'error': 'images 欄位必須為陣列'
            }), 400
        
        if len(images) == 0:
            return jsonify({
                'success': False,
                'error': 'images 陣列不可為空'
            }), 400
        
        # 驗證每個圖片物件的格式
        for idx, item in enumerate(images):
            if not isinstance(item, dict):
                return jsonify({
                    'success': False,
                    'error': f'images[{idx}] 必須為物件'
                }), 400
            
            if 'id' not in item:
                return jsonify({
                    'success': False,
                    'error': f'images[{idx}] 缺少 id 欄位'
                }), 400
            
            if 'image' not in item:
                return jsonify({
                    'success': False,
                    'error': f'images[{idx}] 缺少 image 欄位'
                }), 400
                
            if not isinstance(item['image'], str) or not item['image']:
                return jsonify({
                    'success': False,
                    'error': f'images[{idx}].image 必須為非空字串'
                }), 400
        
        # 執行批次護照辨識
        results = await _process_batch_recognition(images)
        
        # 統計成功與失敗數量
        successful_count = sum(1 for r in results if r['success'])
        failed_count = len(results) - successful_count
        
        return jsonify({
            'success': True,
            'data': {
                'results': results,
                'total': len(results),
                'successful': successful_count,
                'failed': failed_count
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'請求參數錯誤: {str(e)}'
        }), 400
    except RuntimeError as e:
        return jsonify({
            'success': False,
            'error': f'辨識服務錯誤: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'未預期的錯誤: {str(e)}'
        }), 500


async def _process_batch_recognition(images: list[dict[str, str]]) -> list[dict[str, Any]]:
    """處理批次護照辨識
    
    將圖片分批處理，每批次最多處理 BATCH_SIZE 張圖片。
    使用 Semaphore 控制同時處理的圖片數量，避免 API 節流。
    
    Args:
        images (list[dict[str, str]]): 包含 id 與 image 的字典列表
    
    Returns:
        list[dict[str, Any]]: 每張圖片的辨識結果列表
    
    Examples:
        >>> images = [
        ...     {'id': 'img1', 'image': 'base64_string_1'},
        ...     {'id': 'img2', 'image': 'base64_string_2'}
        ... ]
        >>> results = await _process_batch_recognition(images)
        >>> len(results) == 2
        True
    
    Raises:
        此函數不會拋出錯誤，所有錯誤都會在結果中標記
    """
    all_results: list[dict[str, Any]] = []
    
    # 使用 Semaphore 控制同時處理的圖片數量
    semaphore = asyncio.Semaphore(IMAGE_CONCURRENCY)
    
    batch_start_time = time.perf_counter()
    logger.info(f"開始批次辨識: 共 {len(images)} 張圖片, IMAGE_CONCURRENCY={IMAGE_CONCURRENCY}")
    
    # 分批處理
    for batch_start in range(0, len(images), BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, len(images))
        batch_items = images[batch_start:batch_end]
        
        # 建立當前批次的非同步任務（帶有 Semaphore 控制）
        tasks = [
            _recognize_single_image_with_semaphore(semaphore, item['id'], item['image'])
            for item in batch_items
        ]
        
        # 並發執行當前批次
        batch_results = await asyncio.gather(*tasks)
        all_results.extend(batch_results)
    
    batch_elapsed = time.perf_counter() - batch_start_time
    successful_count = sum(1 for r in all_results if r['success'])
    avg_time_per_image = batch_elapsed / len(all_results) if all_results else 'N/A'
    logger.info(
        f"批次辨識完成: 總耗時={batch_elapsed:.2f}s, "
        f"成功={successful_count}/{len(all_results)}, "
        f"平均每張={avg_time_per_image:.2f}s"
    )
    
    return all_results


async def _recognize_single_image_with_semaphore(
    semaphore: asyncio.Semaphore,
    image_id: str,
    base64_image: str
) -> dict[str, Any]:
    """使用 Semaphore 控制併發的單張護照圖片辨識
    
    Args:
        semaphore (asyncio.Semaphore): 用於控制併發數量的 Semaphore
        image_id (str): 圖片的識別碼
        base64_image (str): BASE64 編碼的圖片字串
    
    Returns:
        dict[str, Any]: 辨識結果字典，包含 id、success、data 或 error
    
    Examples:
        >>> semaphore = asyncio.Semaphore(5)
        >>> result = await _recognize_single_image_with_semaphore(semaphore, "img1", "base64_string")
        >>> 'id' in result and 'success' in result
        True
    
    Raises:
        此函數不會拋出錯誤，錯誤會記錄在返回的字典中
    """
    async with semaphore:
        return await _recognize_single_image(image_id, base64_image)


async def _recognize_single_image(image_id: str, base64_image: str) -> dict[str, Any]:
    """辨識單張護照圖片
    
    Args:
        image_id (str): 圖片的識別碼
        base64_image (str): BASE64 編碼的圖片字串
    
    Returns:
        dict[str, Any]: 辨識結果字典，包含 id、success、data 或 error
    
    Examples:
        >>> result = await _recognize_single_image("img1", "base64_string")
        >>> 'id' in result and 'success' in result
        True
    
    Raises:
        此函數不會拋出錯誤，所有錯誤都會在結果中標記
    """
    start_time = time.perf_counter()
    try:
        passport_data = await passport_service.recognize_from_base64(base64_image)
        elapsed = time.perf_counter() - start_time
        logger.debug(f"圖片 {image_id} 辨識成功: 耗時={elapsed:.2f}s")
        return {
            'id': image_id,
            'success': True,
            'data': passport_data
        }
    except ValueError as e:
        elapsed = time.perf_counter() - start_time
        logger.warning(f"圖片 {image_id} 參數錯誤: 耗時={elapsed:.2f}s, 錯誤={str(e)}")
        return {
            'id': image_id,
            'success': False,
            'error': f'請求參數錯誤: {str(e)}'
        }
    except RuntimeError as e:
        elapsed = time.perf_counter() - start_time
        logger.warning(f"圖片 {image_id} 辨識錯誤: 耗時={elapsed:.2f}s, 錯誤={str(e)}")
        return {
            'id': image_id,
            'success': False,
            'error': f'辨識服務錯誤: {str(e)}'
        }


@app.route('/health', methods=['GET'])
def health_check() -> tuple[dict[str, str], int]:
    """健康檢查端點
    
    用於確認服務是否正常運行。
    
    Returns:
        tuple[dict[str, str], int]: JSON 回應和 HTTP 狀態碼
    
    Examples:
        >>> # 使用 curl 測試
        >>> # curl http://localhost:8080/health
    
    Raises:
        此函數不會拋出錯誤
    """
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
