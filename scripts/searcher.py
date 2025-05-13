import os
import re
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
    
    def search(self, query, filters=None, limit=5, search_type='vector'):
        """
        텍스트 쿼리로 KDS 문단 검색
        
        Args:
            query (str): 검색 쿼리
            filters (dict, optional): 메타데이터 필터 조건 (예: {'type': 'header'})
            limit (int, optional): 반환할 최대 결과 수
            search_type (str, optional): 검색 유형 ('vector', 'keyword', 'hybrid')
            
        Returns:
            list: 검색 결과 리스트
        """
        if not query:
            return []
        
        if search_type == 'keyword':
            # 키워드 검색만 수행
            return self.keyword_search(query, filters, limit)
        elif search_type == 'hybrid':
            # 하이브리드 검색 (벡터 + 키워드)
            return self.hybrid_search(query, filters, limit)
        else:
            # 기본 벡터 검색
            query_vector = self.embedder.embed_text(query)
            results = self.vector_db.search(
                query_vector=query_vector,
                filters=filters,
                limit=limit
            )
            
            # 소스 표시 추가
            for result in results:
                result['source'] = 'vector'
                
            return results
    
    def keyword_search(self, query, filters=None, limit=5):
        """
        키워드 기반 텍스트 검색 수행
        
        Args:
            query (str): 검색 쿼리
            filters (dict, optional): 메타데이터 필터 조건
            limit (int, optional): 반환할 최대 결과 수
            
        Returns:
            list: 검색 결과 리스트
        """
        if not query:
            return []
        
        # 키워드 검색을 위해 문서 내용을 가져옴
        try:
            # 필터 설정
            where = {}
            if filters:
                for key, value in filters.items():
                    where[key] = value
            
            # 문서 가져오기 (최대 1000개)
            all_records = self.vector_db.collection.get(
                where=where if where else None,
                limit=1000
            )
            
            if not all_records or 'documents' not in all_records or not all_records['documents']:
                return []
            
            # 쿼리 키워드 분리
            keywords = query.lower().split()
            
            # 정규 표현식 패턴 생성
            patterns = [re.compile(re.escape(keyword), re.IGNORECASE) for keyword in keywords]
            
            # 검색 결과 저장
            results = []
            
            # 모든 문서에 대해 검색
            for i, doc in enumerate(all_records['documents']):
                doc_text = doc.lower()
                
                # 키워드 매칭 점수 계산
                match_count = 0
                for pattern in patterns:
                    match_count += len(pattern.findall(doc_text))
                
                # 하나 이상의 키워드가 포함된 경우만 결과에 추가
                if match_count > 0:
                    # 거리 점수 계산 (적을수록 더 유사)
                    distance = 1.0 - (match_count / (len(keywords) * 3))  # 최대 점수 정규화
                    distance = max(0.01, min(0.99, distance))  # 범위 제한
                    
                    result = {
                        'id': all_records['ids'][i],
                        'text': doc,
                        'metadata': all_records['metadatas'][i] if 'metadatas' in all_records else {},
                        'distance': distance,
                        'match_count': match_count,
                        'source': 'keyword'
                    }
                    results.append(result)
            
            # 거리 기준으로 정렬
            results.sort(key=lambda x: x['distance'])
            
            # 상위 결과만 반환
            return results[:limit]
            
        except Exception as e:
            print(f"키워드 검색 오류: {e}")
            return []
    
    def hybrid_search(self, query, filters=None, limit=5, vector_weight=0.6):
        """
        하이브리드 검색 수행 (벡터 검색 + 키워드 검색)
        
        Args:
            query (str): 검색 쿼리
            filters (dict, optional): 메타데이터 필터 조건
            limit (int, optional): 반환할 최대 결과 수
            vector_weight (float, optional): 벡터 검색 결과의 가중치 (0.0 ~ 1.0)
            
        Returns:
            list: 검색 결과 리스트
        """
        if not query:
            return []
        
        # 각각의 검색 수행 (더 많은 결과를 가져와서 병합 후 필터링)
        keyword_results = self.keyword_search(query, filters, limit=limit*2)
        
        # 벡터 검색
        query_vector = self.embedder.embed_text(query)
        vector_results = self.vector_db.search(
            query_vector=query_vector,
            filters=filters,
            limit=limit*2
        )
        
        # 벡터 검색 결과에 소스 표시 추가
        for result in vector_results:
            result['source'] = 'vector'
        
        # 결과 병합 (ID 기준 중복 제거)
        results_dict = {}
        
        # 벡터 검색 결과 먼저 추가
        for result in vector_results:
            result_id = result['id']
            results_dict[result_id] = result
        
        # 키워드 검색 결과 병합
        for result in keyword_results:
            result_id = result['id']
            if result_id in results_dict:
                # 이미 벡터 검색에서 발견된 결과면 점수 조정
                vector_score = results_dict[result_id]['distance']
                keyword_score = result['distance']
                
                # 하이브리드 점수 계산 (낮을수록 더 유사)
                hybrid_score = (vector_score * vector_weight) + (keyword_score * (1 - vector_weight))
                
                # 기존 결과 업데이트
                results_dict[result_id]['distance'] = hybrid_score
                results_dict[result_id]['source'] = 'hybrid'
                results_dict[result_id]['match_count'] = result.get('match_count', 0)
            else:
                # 벡터 검색에 없는 결과면 추가
                results_dict[result_id] = result
        
        # 딕셔너리를 리스트로 변환
        combined_results = list(results_dict.values())
        
        # 거리 기준으로 정렬 (거리가 작을수록 유사도 높음)
        combined_results.sort(key=lambda x: x['distance'])
        
        # 상위 결과만 반환
        return combined_results[:limit]
    
    def search_by_type(self, query, type_value, limit=5, search_type='vector'):
        """
        문단 유형 별 검색
        
        Args:
            query (str): 검색 쿼리
            type_value (str): 문단 유형 ('header', 'paragraph', 'glossary' 등)
            limit (int, optional): 반환할 최대 결과 수
            search_type (str, optional): 검색 유형 ('vector', 'keyword', 'hybrid')
            
        Returns:
            list: 검색 결과 리스트
        """
        filters = {"type": type_value}
        return self.search(query, filters=filters, limit=limit, search_type=search_type)
    
    def search_headers(self, query, level=None, limit=5, search_type='vector'):
        """
        헤더 검색
        
        Args:
            query (str): 검색 쿼리
            level (int, optional): 헤더 레벨 (없으면 모든 레벨)
            limit (int, optional): 반환할 최대 결과 수
            search_type (str, optional): 검색 유형 ('vector', 'keyword', 'hybrid')
            
        Returns:
            list: 검색 결과 리스트
        """
        filters = {"type": "header"}
        if level is not None:
            filters["level"] = level
        
        return self.search(query, filters=filters, limit=limit, search_type=search_type)
    
    def search_by_doc_id(self, query, doc_id, limit=5, search_type='vector'):
        """
        특정 문서 내에서 검색
        
        Args:
            query (str): 검색 쿼리
            doc_id (str): 문서 ID
            limit (int, optional): 반환할 최대 결과 수
            search_type (str, optional): 검색 유형 ('vector', 'keyword', 'hybrid')
            
        Returns:
            list: 검색 결과 리스트
        """
        filters = {"doc_id": doc_id}
        return self.search(query, filters=filters, limit=limit, search_type=search_type)
    
    def get_db_info(self):
        """
        벡터 DB 정보 조회
        
        Returns:
            dict: 컬렉션 정보
        """
        return self.vector_db.get_collection_info() 