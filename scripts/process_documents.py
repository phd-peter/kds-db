#!/usr/bin/env python
"""
문서 처리 유틸리티 스크립트
- 마크다운 파일을 문단 단위 JSON으로 변환
- 마크다운 파일에서 용어집 추출
- 용어집 JSON 생성
"""

import os
import argparse
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys

from preprocess_glossary_terms import extract_glossary_terms
from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드

def parse_markdown_to_paragraphs(md_path):
    """
    마크다운 파일을 문단 단위로 파싱하여 JSON 형식으로 변환
    
    Args:
        md_path (str): 마크다운 파일 경로
        
    Returns:
        list: 문단 단위 데이터 리스트
    """
    doc_id = os.path.splitext(os.path.basename(md_path))[0]
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 헤더 패턴 (# 제목, ## 제목, ### 제목 등)
    header_pattern = r'^(#{1,6})\s+(.+)$'
    
    # 문서를 줄 단위로 분할
    lines = content.split('\n')
    
    paragraphs = []
    current_paragraph = None
    current_level = 0
    para_id_counter = 1
    
    for line in lines:
        # 헤더 확인
        header_match = re.match(header_pattern, line, re.MULTILINE)
        
        if header_match:
            # 이전 단락이 있으면 저장
            if current_paragraph and current_paragraph['text'].strip():
                current_paragraph['text'] = current_paragraph['text'].strip()
                paragraphs.append(current_paragraph)
            
            # 새 단락 시작
            header_level = len(header_match.group(1))  # #의 개수
            header_text = header_match.group(2)
            
            current_paragraph = {
                'doc_id': doc_id,
                'para_id': f"{doc_id}_{para_id_counter}",
                'type': 'header',
                'level': header_level,
                'text': header_text
            }
            current_level = header_level
            para_id_counter += 1
        elif line.strip() == "" and current_paragraph and current_paragraph['text'].strip():
            # 빈 줄은 단락 구분으로 처리
            current_paragraph['text'] = current_paragraph['text'].strip()
            paragraphs.append(current_paragraph)
            
            # 새로운 일반 단락 시작
            current_paragraph = {
                'doc_id': doc_id,
                'para_id': f"{doc_id}_{para_id_counter}",
                'type': 'paragraph',
                'text': ""
            }
            para_id_counter += 1
        elif current_paragraph:
            # 기존 단락에 내용 추가
            if current_paragraph['text'] and not current_paragraph['text'].endswith('\n'):
                current_paragraph['text'] += ' '
            current_paragraph['text'] += line.strip()
        else:
            # 첫 비헤더 내용은 일반 단락으로 시작
            current_paragraph = {
                'doc_id': doc_id,
                'para_id': f"{doc_id}_{para_id_counter}",
                'type': 'paragraph',
                'text': line.strip()
            }
            para_id_counter += 1
    
    # 마지막 단락 저장
    if current_paragraph and current_paragraph['text'].strip():
        current_paragraph['text'] = current_paragraph['text'].strip()
        paragraphs.append(current_paragraph)
    
    return paragraphs

def open_file_in_editor(file_path):
    """
    지정된 파일을 시스템 기본 편집기로 엽니다.
    
    Args:
        file_path (str): 열 파일의 경로
    """
    if sys.platform == 'win32':
        os.startfile(file_path)
    elif sys.platform == 'darwin':  # macOS
        subprocess.call(['open', file_path])
    else:  # Linux
        subprocess.call(['xdg-open', file_path])

def process_md_document(md_path, output_dir="output", edit_json=False):
    """
    마크다운 문서 처리:
    1. 문단 단위 JSON 변환
    2. 용어집 추출 및 JSON 생성
    
    Args:
        md_path (str): 마크다운 파일 경로
        output_dir (str, optional): 결과물 저장 디렉토리
        edit_json (bool, optional): JSON 파일을 편집기로 열지 여부
        
    Returns:
        tuple: (성공 여부, 문단 JSON 파일 경로, 용어집 파일 경로)
    """
    # 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # 파일 확인
    if not os.path.exists(md_path):
        print(f"오류: 파일을 찾을 수 없습니다: {md_path}")
        return False, None, None
    
    # 문서 ID 추출
    doc_id = os.path.splitext(os.path.basename(md_path))[0]
    
    # 문단 단위 파싱 및 JSON 생성
    paragraphs = parse_markdown_to_paragraphs(md_path)
    if not paragraphs:
        print(f"경고: '{md_path}'에서 문단을 파싱할 수 없습니다.")
        return False, None, None
    
    # 문단 JSON 저장
    paragraphs_path = os.path.join(output_dir, f"{doc_id}.json")
    with open(paragraphs_path, 'w', encoding='utf-8') as f:
        json.dump(paragraphs, f, ensure_ascii=False, indent=2)
    
    print(f"문단 JSON 생성 완료: {len(paragraphs)}개 문단 ({paragraphs_path})")
    
    # 용어집 추출
    glossary_terms = extract_glossary_terms(md_path)
    glossary_path = None
    
    if glossary_terms:
        # 용어집 JSON 저장
        glossary_path = os.path.join(output_dir, f"{doc_id}_glossary.json")
        with open(glossary_path, 'w', encoding='utf-8') as f:
            json.dump(glossary_terms, f, ensure_ascii=False, indent=2)
        
        print(f"용어집 추출 완료: {len(glossary_terms)}개 용어 ({glossary_path})")
    else:
        print(f"경고: '{md_path}'에서 용어집을 추출할 수 없습니다.")
    
    # JSON 파일 수동 편집 옵션
    if edit_json and paragraphs_path:
        print(f"\n===== 수동 편집 단계 시작 =====")
        print(f"텍스트 편집기에서 '{paragraphs_path}' 파일이 열립니다.")
        print(f"필요한 부분을 수정한 후 저장하고 편집기를 닫으세요.")
        print(f"특히 길이가 긴 용어 정의 부분을 제거하는 것이 좋습니다.")
        print(f"수정 작업이 완료되면 Enter 키를 눌러 계속 진행하세요.\n")
        
        # 파일 열기
        open_file_in_editor(paragraphs_path)
        
        # 사용자 입력 대기
        input("파일 편집이 완료되면 Enter 키를 눌러 계속 진행하세요...")
        print(f"수동 편집 완료. 프로세스 계속 진행합니다.")
    
    return True, paragraphs_path, glossary_path

def process_directory(dir_path, output_dir="output", edit_json=False):
    """
    디렉토리 내 모든 마크다운 파일 처리
    
    Args:
        dir_path (str): 마크다운 파일이 있는 디렉토리 경로
        output_dir (str, optional): 결과물 저장 디렉토리
        edit_json (bool, optional): JSON 파일을 편집기로 열지 여부
        
    Returns:
        int: 처리된 문서 수
    """
    # 디렉토리 확인
    if not os.path.isdir(dir_path):
        print(f"오류: 디렉토리를 찾을 수 없습니다: {dir_path}")
        return 0
    
    # 마크다운 파일 검색
    md_files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) 
                if f.endswith('.md') and os.path.isfile(os.path.join(dir_path, f))]
    
    if not md_files:
        print(f"오류: 디렉토리에 마크다운 파일이 없습니다: {dir_path}")
        return 0
    
    print(f"발견된 마크다운 파일 수: {len(md_files)}")
    
    # 각 파일 처리
    success_count = 0
    for file_path in md_files:
        success, _, _ = process_md_document(file_path, output_dir, edit_json)
        if success:
            success_count += 1
    
    print(f"디렉토리 내 문서 처리 완료: {success_count}/{len(md_files)} 성공")
    return success_count

def main():
    """
    메인 함수
    """
    # 커맨드 라인 인자 파싱
    parser = argparse.ArgumentParser(description='마크다운 문서 처리 및 벡터 DB 구축')
    
    # 문서 처리 관련 인자
    document_group = parser.add_argument_group('문서 처리')
    file_group = document_group.add_mutually_exclusive_group()
    file_group.add_argument('--file', type=str, help='처리할 마크다운 파일 경로')
    file_group.add_argument('--directory', type=str, help='처리할 마크다운 파일이 있는 디렉토리 경로')
    document_group.add_argument('--output', type=str, default='output', help='결과물 저장 디렉토리 (기본값: output)')
    document_group.add_argument('--edit', action='store_true', help='JSON 파일 생성 후 수동 편집을 위해 텍스트 편집기 열기')
    
    args = parser.parse_args()
    
    # API 키 확인
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("경고: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("벡터 DB 구축 시 필요하니 나중에 설정해주세요.")
    
    # 문서 처리
    if args.file:
        success, json_path, _ = process_md_document(args.file, args.output, args.edit)
        if success:
            print("\n문서 처리가 완료되었습니다.")
            print(f"생성된 JSON 파일: {json_path}")
            print("\n다음 단계:")
            print("1. (필요한 경우) JSON 파일을 수동으로 편집하여 필요 없는 항목을 제거하세요.")
            print("2. 벡터 DB를 구축하려면 다음 명령어를 실행하세요:")
            print(f"   python scripts/rebuild_vector_db.py")
    elif args.directory:
        success_count = process_directory(args.directory, args.output, args.edit)
        if success_count > 0:
            print("\n문서 처리가 완료되었습니다.")
            print(f"총 {success_count}개 문서 처리 성공")
            print("\n다음 단계:")
            print("1. (필요한 경우) 생성된 JSON 파일을 수동으로 편집하여 필요 없는 항목을 제거하세요.")
            print("2. 벡터 DB를 구축하려면 다음 명령어를 실행하세요:")
            print(f"   python scripts/rebuild_vector_db.py")
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 