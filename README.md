# KDS-DB (Korean Design Standards Database)

이 프로젝트는 한국 디자인 표준(KDS, Korean Design Standards) 문서를 벡터 데이터베이스로 변환하여 검색 가능하게 만드는 도구입니다.

## 프로젝트 개요

KDS-DB는 다음과 같은 기능을 제공합니다:

1. 마크다운(.md) 형식의 KDS 문서를 문단 단위 JSON으로 변환
2. 문서에서 용어집(glossary) 추출 및 JSON 생성 
3. 문단과 용어집을 벡터 DB로 임베딩
4. 웹 기반 검색 인터페이스
5. REST API를 통한 문서 검색 기능

## 설치 방법

### 사전 요구사항

- Python 3.8 이상
- Node.js 14 이상 (웹 UI용)
- OpenAI API 키

### 설치 단계

```bash
# 1. 저장소 클론
git clone https://github.com/yourusername/KDS-DB.git
cd KDS-DB

# 2. Python 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 웹 UI 의존성 설치
cd kds-search-ui
npm install
cd ..

# 5. .env 파일 생성
echo "OPENAI_API_KEY=your-api-key" > .env
```

## 상세 워크플로우

KDS 문서를 벡터 DB로 변환하는 프로세스는 다음 단계를 포함합니다:

### 1. 마크다운 파일 처리 및 JSON 변환

이 단계에서는 마크다운 파일을 문단 단위로 분할하고 용어집을 추출합니다.

```bash
# 단일 마크다운 파일 처리
python scripts/process_documents.py --file markdown-db/142010.md --output output

# 수동 편집 옵션 사용 (권장)
python scripts/process_documents.py --file markdown-db/142010.md --edit

# 또는 디렉토리 내 모든 마크다운 파일 처리
python scripts/process_documents.py --directory markdown-db
```

#### 휴먼 인 더 루프: 문단 JSON 편집

`--edit` 옵션을 사용하면 JSON 생성 후 텍스트 편집기가 열리며, 특히 길이가 긴 용어 정의 부분을 수동으로 제거하여 임베딩 오류를 방지할 수 있습니다.

1. JSON 파일이 시스템 기본 편집기에서 열립니다
2. 필요한 경우 내용 편집 (특히 너무 긴 용어집 정의 부분)
3. 저장 후 편집기 종료
4. Enter 키를 눌러 프로세스 계속 진행

이는 벡터 임베딩 전에 문서 내용을 확인하고 수정할 수 있는 중요한 단계입니다.

### 2. 벡터 DB 구축

이전 단계에서 생성된 JSON 파일을 사용하여 벡터 DB를 구축합니다.

```bash
# 전체 벡터 DB 재구축 (기본 설정)
python scripts/rebuild_vector_db.py

# 또는 옵션 지정
python scripts/rebuild_vector_db.py --json-dir output --vector-db-dir vectordb
```

이 단계에서는 다음과 같은 작업이 수행됩니다:

1. 기존 벡터 DB 디렉터리(`vectordb/`) 삭제
2. 새 벡터 DB 컬렉션 생성
3. 문단 JSON 파일 임베딩 (`output/*.json`)
4. 용어집 JSON 파일 임베딩 (`output/*_glossary.json`)
5. 벡터 DB 컬렉션 정보 출력

JSON 파일만 개별적으로 임베딩하려면 다음 명령어를 사용할 수 있습니다:

```bash
# 단일 문단 JSON 파일 임베딩
python scripts/embed_markdown.py --file output/142010.json

# 단일 용어집 JSON 파일 임베딩
python scripts/embed_glossary.py --file output/142010_glossary.json

# 디렉토리 내 모든 문단 JSON 임베딩
python scripts/embed_markdown.py --directory output

# 디렉토리 내 모든 용어집 JSON 임베딩
python scripts/embed_glossary.py --directory output
```

### 3. 검색 API 서버 실행

벡터 DB에 저장된 문서를 검색할 수 있는，REST API 서버를 실행합니다．

```bash
# 검색 API 서버 실행 (기본 포트: 8000)
python scripts/search_api.py

# 또는 포트 지정
python scripts/search_api.py --port 8080
```

API 엔드포인트:
- `GET /search?q=검색어`: 벡터 DB에서 검색어와 관련된 문단 및 용어 검색
- `GET /health`: API 서버 상태 확인

### 4. 웹 UI 실행

사용자 친화적인 웹 기반 검색 인터페이스를 실행합니다.

```bash
# 웹 UI 개발 서버 실행
cd kds-search-ui
npm run dev
```

웹 UI는 기본적으로 http://localhost:3000에서 접근할 수 있으며, 다음 기능을 제공합니다:
- 키워드 검색
- 검색 결과 정렬 및 필터링
- 문서 내용 확인
- 용어집 참조

## 전체 워크플로우 요약

```
마크다운 파일(.md)
      ↓
process_documents.py → 문단 단위 JSON (.json)
      ↓                용어집 JSON (*_glossary.json)
      ↓
(선택) 수동 편집 (--edit 옵션)
      ↓
rebuild_vector_db.py → 벡터 DB (vectordb/)
      ↓
search_api.py → REST API 서버 (localhost:8000)
      ↓
kds-search-ui (npm run dev) → 웹 인터페이스 (localhost:3000)
```

## 개별 스크립트 상세 설명

### process_documents.py

마크다운 파일을 문단 단위 JSON으로 변환하고 용어집을 추출합니다.

```bash
python scripts/process_documents.py --help
```

주요 옵션:
- `--file`: 처리할 마크다운 파일 경로
- `--directory`: 처리할 마크다운 파일이 있는 디렉토리 경로
- `--output`: 결과물 저장 디렉토리 (기본값: output)
- `--edit`: JSON 파일 생성 후 수동 편집을 위해 텍스트 편집기 열기

### rebuild_vector_db.py

벡터 DB를 처음부터 다시 구축합니다.

```bash
python scripts/rebuild_vector_db.py --help
```

주요 옵션:
- `--json-dir`: JSON 파일이 있는 디렉토리 경로 (기본값: output)
- `--vector-db-dir`: 벡터 DB 디렉토리 경로 (기본값: vectordb)

작동 방식:
1. 기존 vectordb 디렉토리 삭제
2. VectorDB 객체 초기화 (ChromaDB 기반)
3. 문단 및 용어집 컬렉션 자동 생성
4. JSON 파일 로드 및 배치 단위 임베딩
5. 추가된 문서 수 보고

### embed_markdown.py

문단 단위 JSON 파일을 벡터 DB에 임베딩합니다.

```bash
python scripts/embed_markdown.py --help
```

주요 옵션:
- `--file`: 임베딩할 JSON 파일 경로
- `--directory`: 임베딩할 JSON 파일이 있는 디렉토리 경로

성능 개선:
- 단일 `add_document` 호출 대신 배치 처리 사용
- `add_documents` 메서드로 여러 문서 동시 임베딩
- 오류 발생 시 문서 건너뛰고 계속 진행

### embed_glossary.py

용어집 JSON 파일을 벡터 DB에 임베딩합니다.

```bash
python scripts/embed_glossary.py --help
```

주요 옵션:
- `--file`: 임베딩할 용어집 JSON 파일 경로
- `--directory`: 임베딩할 용어집 JSON 파일이 있는 디렉토리 경로

용어집 임베딩 특징:
- 용어와 정의를 결합하여 검색 가능하게 함
- 배치 처리로 성능 최적화
- 메타데이터에 'term' 필드 추가하여 용어 검색 지원

### search_api.py

검색 API 서버를 실행합니다.

```bash
python scripts/search_api.py --help
```

주요 엔드포인트:
- `GET /search?q=검색어`: 문단 및 용어집 컬렉션에서 유사도 검색
- `GET /health`: API 서버 상태 확인
- `GET /collections`: 사용 가능한 컬렉션 목록 반환

## 문제 해결

### 임베딩 오류 (텍스트 너무 김)

용어집이나 긴 문단의 경우 임베딩 오류가 발생할 수 있습니다. 이 문제는 다음과 같이 해결할 수 있습니다:

1. JSON 파일을 수동으로 편집하여 긴 텍스트를 분할하거나 축소
   ```bash
   # 편집기로 JSON 파일 열기
   open output/142010.json  # macOS
   # 또는
   notepad output/142010.json  # Windows
   ```

2. `process_documents.py` 실행 시 `--edit` 옵션을 사용하여 파일을 직접 수정
   ```bash
   python scripts/process_documents.py --file markdown-db/142010.md --edit
   ```

3. 임베딩 시 오류가 발생하는 항목 건너뛰기 - 최신 버전의 스크립트는 오류가 발생해도 계속 진행됨

### 벡터 DB 오류

VectorDB 객체에 create_collection 메서드가 없다는 오류가 발생하는 경우:

1. 최신 버전의 스크립트를 사용하고 있는지 확인하세요.
2. 오래된 벡터 DB를 삭제하고 재구축하세요:
   ```bash
   rm -rf vectordb/
   python scripts/rebuild_vector_db.py
   ```
3. 의존성 패키지가 최신 버전인지 확인하세요:
   ```bash
   pip install --upgrade chromadb
   ```

## 구조 및 컴포넌트

- `markdown-db/`: 원본 마크다운 파일 저장 디렉토리
- `output/`: 변환된 JSON 파일 저장 디렉토리
- `vectordb/`: 벡터 데이터베이스 저장 디렉토리
- `kds-search-ui/`: 웹 검색 인터페이스
- `scripts/`: 처리 스크립트
  - `process_documents.py`: 마크다운 파일 처리 및 JSON 변환
  - `rebuild_vector_db.py`: 벡터 DB 재구축
  - `embed_markdown.py`: 문단 임베딩
  - `embed_glossary.py`: 용어집 임베딩
  - `search_api.py`: 검색 API 서버
  - `vectordb.py`: 벡터 DB 인터페이스 클래스
  - `embedder.py`: 텍스트 임베딩 인터페이스 클래스
  - `preprocess_glossary_terms.py`: 용어집 전처리 유틸리티

## 업데이트 내역

최근 업데이트:
- 문단 JSON 생성과 벡터 DB 임베딩 단계 분리
- 중간에 사용자가 JSON 파일을 수동 편집할 수 있는 "휴먼 인 더 루프" 방식 도입
- `add_document` 대신 `add_documents` 메서드 사용으로 성능 개선 및 배치 처리 구현
- VectorDB 초기화 방식 변경 및 컬렉션 관리 버그 수정
- 용어집 임베딩 프로세스 개선으로 긴 텍스트 처리 능력 향상
- 오류 발생 시에도 임베딩 과정이 중단되지 않도록 예외 처리 강화

## 향후 계획

- 다국어 지원 확장
- 이미지 및 표 추출 기능 개선
- 더 정확한 검색을 위한 고급 임베딩 모델 적용
- 사용자 인터페이스 개선 및 결과 필터링 기능 확장
- 검색 결과 캐싱 및 성능 최적화 