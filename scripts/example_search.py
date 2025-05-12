"""
KDS 문서 임베딩, 벡터 DB 저장 및 검색 예제 스크립트
"""
import os
import json
import time
from embedder import Embedder, load_json_data
from vectordb import VectorDB
from searcher import Searcher
from dotenv import load_dotenv
load_dotenv()  # .env 파일 로드

def load_and_embed_data(json_path, api_key=None, batch_size=1, max_chars=1000):
    """
    JSON 파일에서 데이터 로드 및 임베딩
    
    Args:
        json_path (str): JSON 파일 경로
        api_key (str, optional): OpenAI API 키 
        batch_size (int, optional): 배치 사이즈
        max_chars (int, optional): 텍스트 최대 길이
        
    Returns:
        list: 임베딩된 레코드 리스트
    """
    # JSON 데이터 로드
    print(f"'{json_path}' 파일 로드 중...")
    data = load_json_data(json_path)
    if not data:
        print(f"'{json_path}'에서 데이터를 로드할 수 없습니다.")
        return []
    
    print(f"데이터 로드 완료: {len(data)}개 문단")
    
    # 임베딩 전 텍스트 길이 제한 적용
    for item in data:
        if 'text' in item and len(item['text']) > max_chars:
            item['text'] = item['text'][:max_chars] + "..."
    
    # 임베딩 처리
    print("임베딩 처리 중...")
    embedder = Embedder(api_key=api_key)
    start_time = time.time()
    embedded_data = embedder.embed_batch(data, batch_size=batch_size)
    elapsed_time = time.time() - start_time
    
    print(f"임베딩 완료: {len(embedded_data)}개 문단 (소요 시간: {elapsed_time:.2f}초)")
    return embedded_data

def save_to_vector_db(embedded_data, db_path="./vectordb", collection_name="kds_paragraphs"):
    """
    임베딩된 데이터를 벡터 DB에 저장
    
    Args:
        embedded_data (list): 임베딩된 레코드 리스트
        db_path (str, optional): 벡터 DB 저장 경로
        collection_name (str, optional): 컬렉션 이름
        
    Returns:
        dict: 컬렉션 정보
    """
    print("벡터 DB에 데이터 저장 중...")
    vector_db = VectorDB(db_path=db_path, collection_name=collection_name)
    added_count = vector_db.add_documents(embedded_data)
    print(f"벡터 DB 저장 완료: {added_count}개 문단")
    
    # 컬렉션 정보 조회
    info = vector_db.get_collection_info()
    print(f"컬렉션 정보: {json.dumps(info, ensure_ascii=False, indent=2)}")
    return info

def perform_example_searches(api_key=None, db_path="./vectordb", collection_name="kds_paragraphs"):
    """
    예제 검색 수행
    
    Args:
        api_key (str, optional): OpenAI API 키
        db_path (str, optional): 벡터 DB 저장 경로
        collection_name (str, optional): 컬렉션 이름
    """
    print("\n=== 예제 검색 수행 ===")
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
    
    # 검색 쿼리 예시
    example_queries = [
        "콘크리트 배합 방법",
        "구조설계 도서",
        "안전성 검증",
        "철근 보강"
    ]
    
    # 기본 검색
    for query in example_queries:
        print(f"\n>> 검색 쿼리: '{query}'")
        results = searcher.search(query, limit=3)
        display_results(results)
    
    # 헤더만 검색
    print("\n>> 헤더만 검색: '기본사항'")
    results = searcher.search_headers("기본사항", limit=3)
    display_results(results)
    
    # 특정 문서 내 검색
    print("\n>> 문서 내 검색: 142001에서 '시멘트'")
    results = searcher.search_by_doc_id("시멘트", "142001", limit=3)
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
        print(f"  [{i+1}] ID: {result['id']} (유사도: {result['distance']:.4f})")
        
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
    json_path = "output/142001.json"
    collection_name = "kds_paragraphs"
    
    # 임베딩 및 저장 (이미 처리된 경우 건너뛸 수 있음)
    process = input("문서 임베딩 및 벡터 DB 저장을 수행하시겠습니까? (y/n): ")
    if process.lower() == 'y':
        # 데이터 로드 및 임베딩
        embedded_data = load_and_embed_data(json_path, api_key=api_key, batch_size=1, max_chars=1000)
        if embedded_data:
            # 벡터 DB에 저장
            save_to_vector_db(embedded_data, db_path=db_path, collection_name=collection_name)
    
    # 예제 검색 수행
    perform_example_searches(api_key=api_key, db_path=db_path, collection_name=collection_name)

if __name__ == "__main__":
    main() 