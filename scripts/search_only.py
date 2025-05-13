"""
KDS 문서 벡터 DB 검색 스크립트 - 임베딩 과정 없이 검색만 수행
"""
import os
from searcher import Searcher
from dotenv import load_dotenv
load_dotenv()  # .env 파일 로드

def perform_searches(api_key=None, db_path="./vectordb", collection_name="kds_paragraphs", query=None, search_type='hybrid'):
    """
    벡터 DB에서 검색 수행
    
    Args:
        api_key (str, optional): OpenAI API 키
        db_path (str, optional): 벡터 DB 저장 경로
        collection_name (str, optional): 컬렉션 이름
        query (str, optional): 검색 쿼리. 지정하지 않으면 예제 쿼리 사용
        search_type (str, optional): 검색 유형 ('vector', 'keyword', 'hybrid')
    """
    print("\n=== 벡터 DB 검색 수행 ===")
    print(f"=== 검색 유형: {search_type} ===")
    
    searcher = Searcher(
        api_key=api_key,
        db_path=db_path,
        collection_name=collection_name
    )
    
    # 벡터 DB 정보 출력
    print("\n=== 벡터 DB 정보 ===")
    info = searcher.get_db_info()
    print(f"컬렉션 크기: {info.get('count', 0)}")
    print(f"메타데이터: {info.get('metadata', {})}")
    
    # 문단 유형 확인
    try:
        # 간단하게 몇 개의 레코드 가져와서 유형 확인
        all_records = searcher.vector_db.collection.get(limit=5)
        if 'metadatas' in all_records and all_records['metadatas']:
            print("\n>> 저장된 레코드 유형 확인:")
            types = {}
            for metadata in all_records['metadatas']:
                record_type = metadata.get('type', 'unknown')
                types[record_type] = types.get(record_type, 0) + 1
            for type_name, count in types.items():
                print(f"  {type_name}: {count}개 (샘플 기준)")
    except Exception as e:
        print(f"레코드 유형 확인 중 오류: {e}")
    
    # 사용자 지정 쿼리가 있으면 사용, 없으면 예제 쿼리 사용
    if query:
        print(f"\n>> 검색 쿼리: '{query}' (검색 유형: {search_type})")
        results = searcher.search(query, limit=5, search_type=search_type)
        display_results(results)
    else:
        # 검색 쿼리 예시
        example_queries = [
            "콘크리트 배합 방법",
            "구조설계 도서",
            "안전성 검증",
            "철근 보강"
        ]
        
        # 모든 검색 유형으로 첫 번째 쿼리 테스트
        test_query = example_queries[0]
        
        print(f"\n>> 벡터 검색: '{test_query}'")
        results = searcher.search(test_query, limit=3, search_type='vector')
        display_results(results)
        
        print(f"\n>> 키워드 검색: '{test_query}'")
        results = searcher.search(test_query, limit=3, search_type='keyword')
        display_results(results)
        
        print(f"\n>> 하이브리드 검색: '{test_query}'")
        results = searcher.search(test_query, limit=3, search_type='hybrid')
        display_results(results)
        
        # 나머지 쿼리는 선택된 검색 유형으로 수행
        for query in example_queries[1:]:
            print(f"\n>> {search_type} 검색: '{query}'")
            results = searcher.search(query, limit=3, search_type=search_type)
            display_results(results)
        
        # 헤더만 검색
        print(f"\n>> 헤더만 {search_type} 검색: '기본사항'")
        results = searcher.search_headers("기본사항", limit=3, search_type=search_type)
        display_results(results)
        
        # 특정 문서 내 검색
        print(f"\n>> 문서 내 {search_type} 검색: 142001에서 '시멘트'")
        results = searcher.search_by_doc_id("시멘트", "142001", limit=3, search_type=search_type)
        display_results(results)

def display_results(results):
    """
    검색 결과 출력
    
    Args:
        results (list): 검색 결과 리스트
    """
    if not results:
        print("  검색 결과가 없습니다.")
        return
    
    for i, result in enumerate(results):
        # 검색 소스 정보 추가 (vector, keyword, hybrid)
        source_info = f" [{result.get('source', 'unknown')}]"
        # 키워드 매치 정보 추가 (키워드 검색인 경우)
        match_info = f" (매치 수: {result.get('match_count', '-')})" if 'match_count' in result else ""
        
        print(f"  [{i+1}] ID: {result['id']} (유사도: {result['distance']:.4f}){source_info}{match_info}")
        
        # 메타데이터 출력 (가독성 향상)
        if 'metadata' in result:
            metadata = result['metadata']
            # 중요 메타데이터 먼저 출력
            for key in ['type', 'level']:
                if key in metadata and metadata[key] is not None:
                    print(f"      {key}: {metadata[key]}")
        
        # 텍스트는 짧게 표시
        text = result['text']
        if len(text) > 100:
            text = text[:97] + "..."
        print(f"      내용: {text}")
        print()

def main():
    """
    메인 함수
    """
    # 환경변수에서 API 키 가져오기
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY 환경변수를 설정해주세요.")
        return
    
    # 작업 디렉토리 설정
    db_path = "./vectordb"
    collection_name = "kds_paragraphs"
    
    # 사용자 입력 쿼리 받기
    user_query = input("검색할 키워드를 입력하세요 (빈칸 입력 시 예제 검색 실행): ")
    
    # 검색 유형 선택
    search_type_input = input("검색 유형을 선택하세요 (1: 벡터, 2: 키워드, 3: 하이브리드 - 기본값: 3): ")
    
    # 검색 유형 매핑
    search_type_map = {
        '1': 'vector',
        '2': 'keyword',
        '3': 'hybrid'
    }
    search_type = search_type_map.get(search_type_input, 'hybrid')
    
    # 검색 수행
    perform_searches(
        api_key=api_key, 
        db_path=db_path, 
        collection_name=collection_name,
        query=user_query if user_query.strip() else None,
        search_type=search_type
    )

if __name__ == "__main__":
    main() 