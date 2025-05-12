# Vector DB 데이터 모델 및 인덱싱 설계

## 1. 저장 구조 제안

- 각 문단/헤더/용어 정의를 하나의 레코드(document)로 저장
- 용어 정의(`term` 필드가 존재)와 일반 문단을 동일 구조로 저장
- 헤더의 계층 정보(`level`)는 문서 구조 복원 및 목차 생성에 활용
- 리소스(수식/표/이미지) 참조는 `equations`, `tables`, `images` 배열로 관리
- 확장 메타데이터는 `metadata` 객체로 관리

### 예시 JSON
```json
{
  "doc_id": "142001",
  "para_id": "142001_56",
  "type": "paragraph",
  "text": "(1)콘크리트는 KDS 14 20 40 규정을 만족시키도록 배합하여야 할 뿐만 아니라, ...",
  "level": null,
  "term": null,
  "equations": [
    {
      "id": "eq_142001_56_1",
      "latex": "f_{ck}",
      "position": 2
    }
  ],
  "tables": [],
  "images": [],
  "metadata": {
    "created_at": "2024-06-12T10:00:00Z",
    "tags": ["콘크리트", "배합"],
    "source": "KDS 14 20 00"
  }
}
```

- 헤더 예시:
```json
{
  "doc_id": "142001",
  "para_id": "142001_5",
  "type": "header",
  "text": "1.3 기본사항",
  "level": 2,
  "term": null,
  "equations": [],
  "tables": [],
  "images": [],
  "metadata": {
    "created_at": "2024-06-12T10:00:00Z"
  }
}
```

- 용어 정의 예시:
```json
{
  "doc_id": "142001",
  "para_id": "142001_9_1",
  "type": "glossary",
  "text": "언더컷앵커(undercut anchor): 앵커의 묻힌 단부 부위 콘크리트를 도려내고 ...",
  "level": null,
  "term": "언더컷앵커",
  "equations": [],
  "tables": [],
  "images": [],
  "metadata": {
    "created_at": "2024-06-12T10:00:00Z"
  }
}
```

- 리소스 다중 참조 예시:
```json
{
  "doc_id": "142001",
  "para_id": "142001_100",
  "type": "paragraph",
  "text": "이 계산식은 표 3-1과 그림 3-2를 참조하여 f_ck값을 구한다...",
  "level": null,
  "term": null,
  "equations": [
    { "id": "eq_142001_100_1", "latex": "f_{ck} = \\sqrt{\\sigma_c}", "position": 1 }
  ],
  "tables": [
    { "id": "tbl_142001_100_1", "caption": "표 3-1. 강도 계수", "csv_path": "tables/142001_100_1.csv", "position": 2 }
  ],
  "images": [
    { "id": "img_142001_100_1", "caption": "그림 3-2. 응력 선도", "path": "images/142001_100_1.png", "position": 3 }
  ],
  "metadata": {
    "created_at": "2024-06-12T10:00:00Z",
    "tags": ["응력", "강도계수"]
  }
}
```

---

## 2. 인덱싱/검색 구조 제안

### 공통 인덱싱 기준
- Primary ID: `para_id` (문단/용어별 유일)
- Namespace/Partition: `doc_id` (문서별 분리/필터링)
- Vector Field: `vector` (임베딩 결과, DB에서 자동 관리)
- Metadata 필터링: `type`, `level`, `term`, `metadata.*` 등
- 리소스 필터링: `equations` 존재 여부, `tables` 존재 여부, `images` 존재 여부 등

### 벡터DB별 예시

#### Pinecone
- `id`: `para_id`
- `values`: `vector`
- `metadata`: `{ doc_id, type, level, text, term, has_equations, has_tables, has_images, ... }`

#### Weaviate
- Class: `Paragraph`
- Properties: `doc_id`, `para_id`, `type`, `level`, `text`, `term`, `equations`, `tables`, `images`, `metadata`
- Vectorizer: `text` 필드 기준

#### Chroma
- `ids`: [para_id, ...]
- `documents`: [text, ...]
- `metadatas`: [{ doc_id, type, level, term, has_equations, has_tables, has_images, ... }, ...]

---

## 3. 검색/필터링 활용 예시
- 문서별 검색: `doc_id`로 필터
- 헤더만 검색: `type == "header"`
- 특정 계층만: `level == 2` (2단계 헤더만)
- 용어 정의만: `type == "glossary"` 또는 `term != null`
- 수식 포함 문단: `equations != []` 또는 `has_equations == true`
- 표/이미지 포함: `tables != []`, `images != []`
- 특정 태그/주제: `metadata.tags` 필터
- 목차 생성: `type == "header"`로 필터 후 `level`로 정렬
- RAG/챗봇: 쿼리 임베딩 → 벡터 유사도 검색(`vector`)

---

## 4. 확장성
- 리소스 버전 관리: `metadata`에 `version` 필드 추가
- 리소스 해시 관리: 리소스 ID에 해시값 활용 (중복 방지)
- 외부 참조: 리소스 경로에 URI 스키마 사용 가능 (`http://`, `s3://` 등)
- 리소스 메타데이터: 각 리소스 객체에 추가 메타데이터 확장 가능
- 목차/계층 구조는 `level` 활용하여 복원 가능 