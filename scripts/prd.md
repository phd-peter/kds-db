# Overview
KDS-DB 벡터화 프로젝트는 법령, 판례 등 KDS 문서를 벡터 DB에 저장하여 AI 기반 검색, 하이라이팅, 프론트엔드 렌더링, 데이터 재활용성을 극대화하는 시스템을 구축하는 것을 목표로 한다. 이 프로젝트는 대용량 문서의 효율적 검색, 다양한 리소스(수식, 표, 이미지) 관리, 자동화된 데이터 파이프라인을 제공하여 법률/학술/교육 등 다양한 분야에서 활용될 수 있다.

# Core Features
- **HWP → MD 변환**
- HWP 파일을 Markdown(.md) 파일로 변환
  - 수식, 표, 이미지는 별도 파일로 추출 및 데이터베이스화
- **MD → JSON 구조화**
  - 변환된 MD 파일을 문서 ID(doc_id), 문단 ID(para_id) 기준으로 분할 및 JSON화
- 각 문단별로 본문(text)과 리소스 참조(equations, tables, images) 정보를 포함
- **벡터 DB 인덱싱 및 검색**
  - 각 문단의 text를 임베딩하여 벡터 DB에 저장
  - para_id 기준 검색 인덱스, doc_id/para_id로 원문 위치, 하이라이팅, 리소스 참조 가능
- **프론트엔드 렌더링**
  - 문단 본문은 JSON에서 직접 로드, 수식/표/이미지는 참조 경로로 렌더링
- **자동화 파이프라인**
  - 전체 변환 및 업로드 과정을 자동화, 신규 HWP 파일 추가 시 자동 반영
- **리소스 중복 관리 및 해시화**
  - 동일 리소스의 중복 저장 방지, 해시값 기반 파일명 및 참조
- **메타데이터 확장**
  - 태그, 키워드, 출처, 생성일 등 메타데이터 추가
- **에러/누락 검증 및 피드백 루프**
  - 변환 과정의 오류 자동 검증, 프론트엔드 피드백 반영
- **API/서비스화**
  - 검색, 원문/리소스 제공, 하이라이팅 등 기능을 API로 제공

# User Experience
- **User Personas**
  - 법률/학술 연구자, 교육자, 개발자, 일반 사용자
- **Key User Flows**
  - 문서 업로드 → 자동 변환 및 인덱싱 → 검색/질의 → 결과 하이라이팅 및 리소스 렌더링
- **UI/UX Considerations**
  - 빠른 검색 응답, 직관적 하이라이팅, 리소스(수식/표/이미지) 자연스러운 표시, 피드백 기능

# Technical Architecture
- **System Components**
  - 변환기(HWP→MD), 파서(MD→JSON), 리소스 추출기, 벡터 임베딩/DB 업로더, API 서버, 프론트엔드
- **Data Models**
  - 문서/문단(JSON), 리소스(수식/표/이미지), 메타데이터
- **APIs and Integrations**
  - 벡터 DB API(예: Pinecone, Qdrant 등), 파일 스토리지, 프론트엔드 API
- **Infrastructure Requirements**
  - 대용량 파일 저장소, 벡터 DB 서버, 자동화 파이프라인 서버, 프론트엔드 호스팅

# Development Roadmap
- **MVP Requirements**
  - HWP→MD 변환기, MD→JSON 파서, 리소스 추출/저장, 벡터 DB 업로더, 기본 검색 API, 프론트엔드 검색/하이라이팅
- **Future Enhancements**
  - 메타데이터 확장, 리소스 버전 관리, 사용자 피드백 시스템, 고급 검색(필터/스코어링), 외부 서비스 연동(API)

# Logical Dependency Chain
- 1) HWP→MD 변환기 및 리소스 추출기 개발
- 2) MD→JSON 파서 및 데이터 모델 설계
- 3) 벡터 임베딩/DB 업로더 구현
- 4) 기본 검색 API 및 프론트엔드 구축(최소한의 검색/하이라이팅)
- 5) 자동화 파이프라인 통합
- 6) 메타데이터, 피드백, API 등 고도화 기능 추가

# Risks and Mitigations
- **HWP 파싱의 정확도/누락**: 다양한 HWP 문서 포맷 대응, 수동 검증 도구 제공
- **리소스 참조 불일치**: 자동 검증 및 리포트, 해시 기반 중복 방지
- **대용량 데이터 처리**: 분산 처리, 벡터 DB 확장성 고려
- **MVP 범위 산정**: 핵심 기능 우선 개발, 피드백 기반 점진적 확장
- **리소스 관리 복잡성**: 해시화, 버전 관리, 참조 무결성 체크

# Appendix
## 예시 JSON 구조
```json
{
  "doc_id": "law_형법_250",
  "para_id": "형법_250_1",
  "text": "사람을 살해한 자는 사형, 무기 또는 5년 이상의 징역에 처한다.",
  "equations": [ { "id": "eq_250_1", "latex": "...", "position": 2 } ],
  "tables": [ { "id": "tbl_250_1", "caption": "...", "csv_path": "tables/형법250_1.csv", "position": 3 } ],
  "images": [ { "id": "img_250_1", "caption": "...", "path": "images/형법250_그림2-1.png", "position": 5 } ]
}
```

## 참고 자료
- Pinecone, Qdrant, Weaviate 등 주요 벡터 DB 비교
- HWP→MD 오픈소스 변환기, Python 파서 예시
- MathJax, Pandas, React 등 프론트엔드 렌더링 도구 