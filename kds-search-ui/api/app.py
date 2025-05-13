from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # CORS 활성화

# 백엔드 서버 URL 설정
BACKEND_URL = "http://localhost:5000"  # 실제 Python 백엔드 서버 주소

@app.route('/search', methods=['GET'])
def search():
    # 쿼리 파라미터 추출
    query = request.args.get('query', '')
    search_type = request.args.get('search_type', 'hybrid')
    limit = request.args.get('limit', 5)
    
    # Python 백엔드로 검색 요청 전달
    try:
        # search_only.py 서버로 요청 전달
        response = requests.get(
            f"{BACKEND_URL}/search",
            params={
                'query': query,
                'search_type': search_type,
                'limit': limit
            },
            timeout=10
        )
        
        # 응답 확인
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': '검색 서버 오류'}), response.status_code
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5328))
    app.run(host='0.0.0.0', port=port)
