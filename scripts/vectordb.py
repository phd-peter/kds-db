import os
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
load_dotenv()  # .env 파일 로드

class VectorDB:
    """
    ChromaDB를 사용하여 문단 임베딩을 저장하고 검색하는 클래스
    """
    def __init__(self, db_path="./vectordb", collection_name="kds_paragraphs"):
        """
        벡터 DB 초기화
        
        Args:
            db_path (str, optional): 벡터 DB 저장 경로
            collection_name (str, optional): 컬렉션 이름
        """
        # 디렉토리 생성
        os.makedirs(db_path, exist_ok=True)
        
        # ChromaDB 클라이언트 및 컬렉션 설정
        self.client = chromadb.PersistentClient(path=db_path)
        
        # 컬렉션 생성 또는 가져오기
        try:
            self.collection = self.client.get_collection(collection_name)
            print(f"기존 컬렉션 '{collection_name}' 로드됨")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "KDS 문단 벡터 데이터베이스"}
            )
            print(f"새 컬렉션 '{collection_name}' 생성됨")
    
    def add_documents(self, records):
        """
        문단 레코드를 벡터 DB에 추가
        
        Args:
            records (list): 문단 레코드 리스트 (각 레코드는 'vector', 'text', 'para_id' 필드 필요)
            
        Returns:
            int: 추가된 문서 수
        """
        if not records:
            return 0
        
        # ChromaDB 형식에 맞게 데이터 변환
        ids = []
        documents = []
        embeddings = []
        metadatas = []
        
        for record in records:
            if 'para_id' not in record or 'text' not in record or 'vector' not in record:
                print(f"필수 필드가 누락된 레코드 건너뜀: {record.get('para_id', 'unknown')}")
                continue
            
            # 벡터가 비어있는지 확인 추가
            if not record['vector'] or len(record['vector']) == 0:
                print(f"비어있는 벡터를 가진 레코드 건너뜀: {record.get('para_id', 'unknown')}")
                continue
            
            # id, 본문, 임베딩, 메타데이터 분리
            ids.append(str(record['para_id']))
            documents.append(record['text'])
            embeddings.append(record['vector'])
            
            # 메타데이터 추출 (vector 제외한 모든 필드)
            metadata = {k: v for k, v in record.items() if k != 'vector' and k != 'text'}
            metadatas.append(metadata)
        
        if not ids:
            return 0
        
        # 벡터 DB에 추가
        try:
            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            return len(ids)
        except Exception as e:
            print(f"문서 추가 오류: {e}")
            return 0
    
    def search(self, query_text=None, query_vector=None, filters=None, limit=5):
        """
        벡터 DB에서 유사도 검색 수행
        
        Args:
            query_text (str, optional): 검색 쿼리 텍스트
            query_vector (list, optional): 검색 쿼리 임베딩 벡터
            filters (dict, optional): 메타데이터 필터 조건
            limit (int, optional): 반환할 최대 결과 수
            
        Returns:
            list: 검색 결과 리스트
        """
        if query_text is None and query_vector is None:
            raise ValueError("쿼리 텍스트 또는 쿼리 벡터가 필요합니다.")
        
        # 필터 설정
        where = {}
        if filters:
            for key, value in filters.items():
                where[key] = value
        
        # ChromaDB 검색 수행
        try:
            if query_vector:
                # 벡터로 검색
                results = self.collection.query(
                    query_embeddings=[query_vector],
                    where=where if where else None,
                    n_results=limit
                )
            else:
                # 텍스트로 검색
                results = self.collection.query(
                    query_texts=[query_text],
                    where=where if where else None,
                    n_results=limit
                )
            
            # 검색 결과 변환
            formatted_results = []
            
            # 결과가 있는 경우
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    item = {
                        'id': results['ids'][0][i],
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    }
                    formatted_results.append(item)
            
            return formatted_results
            
        except Exception as e:
            print(f"검색 오류: {e}")
            return []
    
    def get_collection_info(self):
        """
        컬렉션 정보 반환
        
        Returns:
            dict: 컬렉션 정보
        """
        try:
            count = self.collection.count()
            return {
                'name': self.collection.name,
                'count': count,
                'metadata': self.collection.metadata
            }
        except Exception as e:
            print(f"컬렉션 정보 조회 오류: {e}")
            return {'error': str(e)} 