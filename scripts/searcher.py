import os
from embedder import Embedder
from vectordb import VectorDB
from dotenv import load_dotenv
load_dotenv()  # .env 파일 로드

class Searcher:
    """
    텍스트 쿼리를 사용하여 KDS 문단 검색 기능 제공
    """
    def __init__(self, api_key=None, db_path="./vectordb", collection_name="kds_paragraphs"):
        """
        검색 엔진 초기화
        
        Args:
            api_key (str, optional): OpenAI API 키. 없으면 환경변수에서 가져옴
            db_path (str, optional): 벡터 DB 저장 경로
            collection_name (str, optional): 컬렉션 이름
        """
        # 임베더 초기화
        self.embedder = Embedder(api_key=api_key)
        
        # 벡터 DB 초기화
        self.vector_db = VectorDB(db_path=db_path, collection_name=collection_name)
    
    def search(self, query, filters=None, limit=5):
        """
        텍스트 쿼리로 KDS 문단 검색
        
        Args:
            query (str): 검색 쿼리
            filters (dict, optional): 메타데이터 필터 조건 (예: {'type': 'header'})
            limit (int, optional): 반환할 최대 결과 수
            
        Returns:
            list: 검색 결과 리스트
        """
        if not query:
            return []
        
        # 쿼리 임베딩 생성
        query_vector = self.embedder.embed_text(query)
        
        # 벡터 DB 검색
        results = self.vector_db.search(
            query_vector=query_vector,
            filters=filters,
            limit=limit
        )
        
        return results
    
    def search_by_type(self, query, type_value, limit=5):
        """
        문단 유형 별 검색
        
        Args:
            query (str): 검색 쿼리
            type_value (str): 문단 유형 ('header', 'paragraph', 'glossary' 등)
            limit (int, optional): 반환할 최대 결과 수
            
        Returns:
            list: 검색 결과 리스트
        """
        filters = {"type": type_value}
        return self.search(query, filters=filters, limit=limit)
    
    def search_headers(self, query, level=None, limit=5):
        """
        헤더 검색
        
        Args:
            query (str): 검색 쿼리
            level (int, optional): 헤더 레벨 (없으면 모든 레벨)
            limit (int, optional): 반환할 최대 결과 수
            
        Returns:
            list: 검색 결과 리스트
        """
        filters = {"type": "header"}
        if level is not None:
            filters["level"] = level
        
        return self.search(query, filters=filters, limit=limit)
    
    def search_by_doc_id(self, query, doc_id, limit=5):
        """
        특정 문서 내에서 검색
        
        Args:
            query (str): 검색 쿼리
            doc_id (str): 문서 ID
            limit (int, optional): 반환할 최대 결과 수
            
        Returns:
            list: 검색 결과 리스트
        """
        filters = {"doc_id": doc_id}
        return self.search(query, filters=filters, limit=limit)
    
    def get_db_info(self):
        """
        벡터 DB 정보 조회
        
        Returns:
            dict: 컬렉션 정보
        """
        return self.vector_db.get_collection_info() 