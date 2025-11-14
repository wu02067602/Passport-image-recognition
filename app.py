"""護照辨識 API 應用程式

此模組提供 Flask API 用於護照辨識。
"""

from flask import Flask, request, jsonify
from typing import Any

from src.passport_service import PassportService


app = Flask(__name__)
passport_service = PassportService()


@app.route('/api/passport/recognize', methods=['POST'])
def recognize_passport() -> tuple[dict[str, Any], int]:
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
        >>> # curl -X POST http://localhost:5000/api/passport/recognize \
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
        
        if not isinstance(base64_image, str) or not base64_image:
            return jsonify({
                'success': False,
                'error': 'image 欄位必須為非空字串'
            }), 400
        
        # 執行護照辨識
        passport_data = passport_service.recognize_from_base64(base64_image)
        
        return jsonify({
            'success': True,
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


@app.route('/health', methods=['GET'])
def health_check() -> tuple[dict[str, str], int]:
    """健康檢查端點
    
    用於確認服務是否正常運行。
    
    Returns:
        tuple[dict[str, str], int]: JSON 回應和 HTTP 狀態碼
    
    Examples:
        >>> # 使用 curl 測試
        >>> # curl http://localhost:5000/health
    
    Raises:
        此函數不會拋出錯誤
    """
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
