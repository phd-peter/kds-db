#!/usr/bin/env python
"""
벡터 DB를 처음부터 다시 구축하는 스크립트
"""

import argparse
import os
import shutil
import glob
from typing import Optional, List

from vectordb import VectorDB
from embed_markdown import embed_file as embed_markdown_file
from embed_glossary import embed_file as embed_glossary_file
from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드

def rebuild_vector_db(
    json_dir: str = 'output',
    vector_db_dir: str = 'vectordb',
    api_key: Optional[str] = None
) -> None:
    """
    벡터 DB를 처음부터 다시 구축합니다.
    
    Args:
        json_dir (str): JSON 파일이 있는 디렉토리 경로
        vector_db_dir (str): 벡터 DB 디렉토리 경로
        api_key (str, optional): OpenAI API 키
    """
    print("벡터 DB 재구축 시작")
    
    # 기존 벡터 DB 삭제
    if os.path.exists(vector_db_dir):
        print(f"기존 벡터 DB 삭제 중: {vector_db_dir}")
        shutil.rmtree(vector_db_dir)
    
    # 문단 JSON 파일 찾기
    paragraph_files = [f for f in glob.glob(f"{json_dir}/*.json") if not f.endswith("_glossary.json")]
    if not paragraph_files:
        print(f"오류: {json_dir} 디렉토리에 문단 JSON 파일이 없습니다.")
        return
    
    # 용어집 JSON 파일 찾기
    glossary_files = glob.glob(f"{json_dir}/*_glossary.json")
    
    print(f"문단 JSON 파일 수: {len(paragraph_files)}")
    print(f"용어집 JSON 파일 수: {len(glossary_files)}")
    
    # 새로운 벡터 DB 디렉토리 생성
    os.makedirs(vector_db_dir, exist_ok=True)
    
    # 각 문단 파일 임베딩
    for file_path in paragraph_files:
        try:
            print(f"\n문단 파일 임베딩: {file_path}")
            embed_markdown_file(file_path, api_key)
        except Exception as e:
            print(f"오류: 문단 파일 임베딩 중 오류 발생: {e}")
    
    # 각 용어집 파일 임베딩
    for file_path in glossary_files:
        try:
            print(f"\n용어집 파일 임베딩: {file_path}")
            embed_glossary_file(file_path, api_key)
        except Exception as e:
            print(f"오류: 용어집 파일 임베딩 중 오류 발생: {e}")
    
    print("\n벡터 DB 구축 완료")
    
    # 컬렉션 정보 출력
    try:
        vector_db = VectorDB()
        collection_info = vector_db.get_collection_info()
        print(f"\n벡터 DB 컬렉션 정보:")
        print(f"- 문단 컬렉션 (kds_paragraphs): {collection_info.get('kds_paragraphs', '없음')}")
        print(f"- 용어집 컬렉션 (kds_glossary): {collection_info.get('kds_glossary', '없음')}")
    except Exception as e:
        print(f"오류: 벡터 DB 컬렉션 정보 조회 실패: {e}")

def main():
    """
    메인 함수
    """
    # 커맨드 라인 인자 파싱
    parser = argparse.ArgumentParser(description='벡터 DB 재구축')
    parser.add_argument('--json-dir', type=str, default='output', 
                        help='JSON 파일이 있는 디렉토리 경로 (기본값: output)')
    parser.add_argument('--vector-db-dir', type=str, default='vectordb', 
                        help='벡터 DB 디렉토리 경로 (기본값: vectordb)')
    
    args = parser.parse_args()
    
    # API 키 확인
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("오류: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("벡터 DB 구축을 위해 OpenAI API 키가 필요합니다.")
        return
    
    # 벡터 DB 재구축
    rebuild_vector_db(
        json_dir=args.json_dir,
        vector_db_dir=args.vector_db_dir,
        api_key=api_key
    )

if __name__ == "__main__":
    main() 