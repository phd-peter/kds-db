import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()  # .env 파일 로드


class Embedder:
    """
    OpenAI API를 사용하여 텍스트를 벡터로 임베딩하는 클래스
    """
    def __init__(self, api_key=None, model="text-embedding-3-small"):
        """
        임베더 초기화
        
        Args:
            api_key (str, optional): OpenAI API 키. 없으면 환경변수에서 가져옴
            model (str, optional): 사용할 임베딩 모델
        """
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key is None:
                raise ValueError("OpenAI API 키가 필요합니다. 환경변수 OPENAI_API_KEY를 설정하거나 api_key를 전달하세요.")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def embed_text(self, text):
        """
        단일 텍스트를 임베딩 벡터로 변환
        
        Args:
            text (str): 임베딩할 텍스트
            
        Returns:
            list: 임베딩 벡터
        """
        if not text or not isinstance(text, str):
            return []
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"임베딩 오류: {e}")
            return []
    
    def embed_batch(self, records, batch_size=20):
        """
        문단 레코드 배치를 임베딩 처리
        
        Args:
            records (list): 문단 레코드 리스트 (각 레코드는 최소한 'text' 필드 포함 필요)
            batch_size (int, optional): API 호출당 처리할 텍스트 수
            
        Returns:
            list: 임베딩 벡터가 추가된 레코드 리스트
        """
        if not records:
            return []
        
        results = []
        # 작은 배치로 나누어 처리
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            texts = [record['text'] for record in batch]
            
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=texts
                )
                
                # 벡터와 원본 레코드 결합
                for j, record in enumerate(batch):
                    record_copy = record.copy()
                    vector = response.data[j].embedding
                    # 벡터가 비어있지 않은지 확인
                    if vector and len(vector) > 0:
                        record_copy['vector'] = vector
                        results.append(record_copy)
                    else:
                        print(f"경고: 비어있는 벡터 발견: {record.get('para_id', 'unknown')}")
                
                # API 속도 제한 고려 (초당 요청 수)
                if i + batch_size < len(records):
                    time.sleep(0.5)
                    
            except Exception as e:
                print(f"배치 임베딩 오류: {e}")
                # 오류 시 개별 처리로 대체
                for record in batch:
                    record_copy = record.copy()
                    record_copy['vector'] = self.embed_text(record['text'])
                    results.append(record_copy)
        
        return results

def load_json_data(file_path):
    """
    JSON 파일에서 데이터 로드
    
    Args:
        file_path (str): JSON 파일 경로
        
    Returns:
        list: JSON 데이터
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"파일 로드 오류: {e}")
        return []

# 테스트 코드
if __name__ == "__main__":
    # API 키 설정 테스트
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        print("API 키 설정됨")
        
        # 간단한 임베딩 테스트
        embedder = Embedder(api_key=api_key)
        vector = embedder.embed_text("안녕하세요, 벡터 임베딩 테스트입니다.")
        print(f"임베딩 벡터 길이: {len(vector)}")
        print(f"처음 5개 요소: {vector[:5]}")
    else:
        print("OPENAI_API_KEY 환경변수를 설정해주세요.") 