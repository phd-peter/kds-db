from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from searcher import Searcher
from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드

app = Flask(__name__)
CORS(app)  # CORS 활성화

@app.route('/search', methods=['GET'])
def search():
    # 쿼리 파라미터 추출
    query = request.args.get('query', '')
    search_type = request.args.get('search_type', 'hybrid')
    limit = int(request.args.get('limit', 5))
    
    if not query:
        return jsonify({'results': [], 'message': '검색어를 입력하세요.'}), 400
    
    # API 키 환경변수에서 로드
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return jsonify({'error': 'API 키가 설정되지 않았습니다.'}), 500
    
    # 벡터 DB 디렉토리 설정
    db_path = "./vectordb"
    collection_name = "kds_paragraphs"
    
    # Searcher 초기화
    searcher = Searcher(
        api_key=api_key,
        db_path=db_path,
        collection_name=collection_name
    )
    
    try:
        # 검색 수행
        results = searcher.search(query, limit=limit, search_type=search_type)
        
        # 결과 반환
        return jsonify({
            'results': results,
            'count': len(results),
            'query': query,
            'search_type': search_type
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
