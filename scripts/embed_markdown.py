#!/usr/bin/env python
"""
마크다운 문서를 벡터 DB에 임베딩하는 스크립트
"""

import os
import glob
import json
from typing import List, Dict, Any, Optional

from vectordb import VectorDB
from embedder import Embedder

def load_paragraphs(json_path: str) -> List[Dict[str, Any]]:
    """
    문단 단위 JSON 파일을 로드합니다.
    
    Args:
        json_path (str): 문단 단위 JSON 파일 경로
    
    Returns:
        List[Dict[str, Any]]: 문단 데이터 리스트
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            paragraphs = json.load(f)
        return paragraphs
    except json.JSONDecodeError:
        print(f"오류: 유효하지 않은 JSON 파일입니다: {json_path}")
        return []
    except Exception as e:
        print(f"오류: 파일 로드 중 오류가 발생했습니다: {e}")
        return []

def embed_file(file_path: str, api_key: Optional[str] = None) -> None:
    """
    단일 JSON 파일을 벡터 DB에 임베딩합니다.
    
    Args:
        file_path (str): JSON 파일 경로
        api_key (str, optional): OpenAI API 키
    """
    print(f"문단 JSON 파일 임베딩 시작: {file_path}")
    
    # 파일 확인
    if not os.path.exists(file_path):
        print(f"오류: 파일을 찾을 수 없습니다: {file_path}")
        return
    
    # JSON 로드
    paragraphs = load_paragraphs(file_path)
    print(f"로드된 문단 수: {len(paragraphs)}")
    
    if not paragraphs:
        print(f"경고: '{file_path}'에서 문단을 로드할 수 없습니다.")
        return
    
    # 임베딩 및 벡터 DB 저장
    embedder = Embedder(api_key)
    collection_name = "kds_paragraphs"
    vector_db = VectorDB(collection_name=collection_name)
    
    # 단락 임베딩
    embedding_count = 0
    batch_size = 10  # 한 번에 처리할 문단 수
    batch_records = []
    
    for para in paragraphs:
        # 메타데이터 준비
        metadata = {
            'doc_id': para.get('doc_id', ''),
            'type': para.get('type', 'paragraph'),
            'level': para.get('level', 0) if para.get('type') == 'header' else 0,
            'para_id': para.get('para_id', '')
        }
        
        try:
            # 텍스트 임베딩
            text = para.get('text', '')
            if not text:
                print(f"경고: 빈 텍스트 건너뛰기: {para.get('para_id', 'unknown')}")
                continue
            
            # 임베딩 벡터 생성
            embedding = embedder.embed_text(text)
            
            # 레코드 구성
            record = {
                'para_id': para.get('para_id', ''),
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
            print(f"오류: 문단 임베딩 중 오류 발생: {para.get('para_id', 'unknown')}: {e}")
    
    # 남은 배치 처리
    if batch_records:
        added = vector_db.add_documents(batch_records)
        embedding_count += added
    
    print(f"임베딩 완료: {embedding_count}/{len(paragraphs)} 문단 처리됨")

def embed_directory(directory_path: str, api_key: Optional[str] = None) -> None:
    """
    디렉토리 내 모든 JSON 파일을 벡터 DB에 임베딩합니다.
    
    Args:
        directory_path (str): JSON 파일이 있는 디렉토리 경로
        api_key (str, optional): OpenAI API 키
    """
    print(f"디렉토리 내 JSON 파일 임베딩 시작: {directory_path}")
    
    # 디렉토리 확인
    if not os.path.isdir(directory_path):
        print(f"오류: 디렉토리를 찾을 수 없습니다: {directory_path}")
        return
    
    # JSON 파일 검색 (용어집 JSON 제외)
    json_files = [
        f for f in glob.glob(os.path.join(directory_path, "*.json"))
        if not f.endswith("_glossary.json")
    ]
    
    if not json_files:
        print(f"오류: 디렉토리에 JSON 파일이 없습니다: {directory_path}")
        return
    
    print(f"발견된 JSON 파일 수: {len(json_files)}")
    
    # 각 파일 임베딩
    for file_path in json_files:
        embed_file(file_path, api_key)
    
    print(f"디렉토리 내 JSON 파일 임베딩 완료")

def main():
    """
    메인 함수
    """
    import argparse
    from dotenv import load_dotenv
    
    load_dotenv()  # .env 파일 로드
    
    # 커맨드 라인 인자 파싱
    parser = argparse.ArgumentParser(description='마크다운 문서를 벡터 DB에 임베딩')
    
    # 파일 또는 디렉토리 지정
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', type=str, help='임베딩할 JSON 파일 경로')
    group.add_argument('--directory', type=str, help='임베딩할 JSON 파일이 있는 디렉토리 경로')
    
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