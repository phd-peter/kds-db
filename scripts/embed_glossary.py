#!/usr/bin/env python
"""
용어집 JSON 파일을 벡터 DB에 임베딩하는 스크립트
"""

import os
import glob
import json
from typing import List, Dict, Any, Optional

from vectordb import VectorDB
from embedder import Embedder

def load_glossary(glossary_path: str) -> List[Dict[str, Any]]:
    """
    용어집 JSON 파일을 로드합니다.
    
    Args:
        glossary_path (str): 용어집 JSON 파일 경로
        
    Returns:
        List[Dict[str, Any]]: 용어집 데이터 리스트
    """
    try:
        with open(glossary_path, 'r', encoding='utf-8') as f:
            glossary_terms = json.load(f)
        return glossary_terms
    except json.JSONDecodeError:
        print(f"오류: 유효하지 않은 JSON 파일입니다: {glossary_path}")
        return []
    except Exception as e:
        print(f"오류: 파일 로드 중 오류가 발생했습니다: {e}")
        return []

def embed_file(file_path: str, api_key: Optional[str] = None) -> None:
    """
    단일 용어집 JSON 파일을 벡터 DB에 임베딩합니다.
    
    Args:
        file_path (str): 용어집 JSON 파일 경로
        api_key (str, optional): OpenAI API 키
    """
    print(f"용어집 파일 임베딩 시작: {file_path}")
    
    # 파일 확인
    if not os.path.exists(file_path):
        print(f"오류: 파일을 찾을 수 없습니다: {file_path}")
        return
    
    # 용어집 로드
    glossary_terms = load_glossary(file_path)
    print(f"로드된 용어 수: {len(glossary_terms)}")
    
    if not glossary_terms:
        print(f"경고: '{file_path}'에서 용어를 로드할 수 없습니다.")
        return
    
    # 임베딩 및 벡터 DB 저장
    embedder = Embedder(api_key)
    collection_name = "kds_glossary"
    vector_db = VectorDB(collection_name=collection_name)
    
    # 용어 임베딩
    embedding_count = 0
    batch_size = 10  # 한 번에 처리할 용어 수
    batch_records = []
    
    for term in glossary_terms:
        # 메타데이터 준비
        metadata = {
            'doc_id': term.get('doc_id', ''),
            'type': 'definition',
            'term': term.get('term', ''),
            'para_id': term.get('para_id', '')
        }
        
        try:
            # 텍스트 임베딩 (용어와 정의를 결합)
            term_text = term.get('term', '')
            definition_text = term.get('text', '')
            
            if not term_text or not definition_text:
                print(f"경고: 비어있는 용어 또는 정의 건너뛰기: {term.get('para_id', 'unknown')}")
                continue
            
            # 검색을 위해 용어와 정의를 결합
            text = f"{term_text}: {definition_text}"
            
            # 임베딩 벡터 생성
            embedding = embedder.embed_text(text)
            
            # 레코드 구성
            record = {
                'para_id': term.get('para_id', ''),
                'text': text,
                'vector': embedding,
                **metadata  # 메타데이터 병합
            }
            
            # 배치에 추가
            batch_records.append(record)
            
            # 배치 크기에 도달하면 처리
            if len(batch_records) >= batch_size:
                added = vector_db.add_documents(batch_records)
                embedding_count += added
                batch_records = []  # 배치 초기화
            
        except Exception as e:
            print(f"오류: 용어 임베딩 중 오류 발생: {term.get('para_id', 'unknown')}: {e}")
    
    # 남은 배치 처리
    if batch_records:
        added = vector_db.add_documents(batch_records)
        embedding_count += added
    
    print(f"임베딩 완료: {embedding_count}/{len(glossary_terms)} 용어 처리됨")

def embed_directory(directory_path: str, api_key: Optional[str] = None) -> None:
    """
    디렉토리 내 모든 용어집 JSON 파일을 벡터 DB에 임베딩합니다.
    
    Args:
        directory_path (str): 용어집 JSON 파일이 있는 디렉토리 경로
        api_key (str, optional): OpenAI API 키
    """
    print(f"디렉토리 내 용어집 파일 임베딩 시작: {directory_path}")
    
    # 디렉토리 확인
    if not os.path.isdir(directory_path):
        print(f"오류: 디렉토리를 찾을 수 없습니다: {directory_path}")
        return
    
    # 용어집 JSON 파일 검색
    glossary_files = glob.glob(os.path.join(directory_path, "*_glossary.json"))
    
    if not glossary_files:
        print(f"오류: 디렉토리에 용어집 JSON 파일이 없습니다: {directory_path}")
        return
    
    print(f"발견된 용어집 파일 수: {len(glossary_files)}")
    
    # 각 파일 임베딩
    for file_path in glossary_files:
        embed_file(file_path, api_key)
    
    print(f"디렉토리 내 용어집 파일 임베딩 완료")

def main():
    """
    메인 함수
    """
    import argparse
    from dotenv import load_dotenv
    
    load_dotenv()  # .env 파일 로드
    
    # 커맨드 라인 인자 파싱
    parser = argparse.ArgumentParser(description='용어집 파일을 벡터 DB에 임베딩')
    
    # 파일 또는 디렉토리 지정
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', type=str, help='임베딩할 용어집 JSON 파일 경로')
    group.add_argument('--directory', type=str, help='임베딩할 용어집 JSON 파일이 있는 디렉토리 경로')
    
    args = parser.parse_args()
    
    # API 키 확인
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("오류: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        return
    
    # 임베딩 실행
    if args.file:
        embed_file(args.file, api_key)
    elif args.directory:
        embed_directory(args.directory, api_key)

if __name__ == "__main__":
    main() 