# Vector DB 스키마 정의서 (필드별)

| 필드명      | 타입         | 필수 | 설명                                                         |
|-------------|--------------|------|--------------------------------------------------------------|
| doc_id      | string       | ✅   | 문서 고유 ID (예: 파일명 등)                                 |
| para_id     | string       | ✅   | 문단 고유 ID (doc_id+순번 등, 전체 데이터에서 유일)           |
| type        | string       | ✅   | 문단 유형 ("header", "paragraph", "glossary" 등)             |
| text        | string       | ✅   | 임베딩/검색 대상이 되는 본문 텍스트                           |
| level       | integer/null | ❌   | 헤더의 계층(level). type이 'header'일 때만 사용              |
| term        | string/null  | ❌   | 용어 정의일 경우 용어명, 일반 문단은 null                    |
| equations   | array/null   | ❌   | 문단 내 수식 참조 목록 [{id, latex, position}, ...]          |
| tables      | array/null   | ❌   | 문단 내 표 참조 목록 [{id, caption, csv_path, position}, ...] |
| images      | array/null   | ❌   | 문단 내 이미지 참조 목록 [{id, caption, path, position}, ...] |
| vector      | array[float] | ❌   | 임베딩 벡터 (DB에 저장 시 자동 생성/입력)                    |
| metadata    | object       | ❌   | 추가 정보(생성일, 태그, 출처 등, 확장 가능)                   |

> vector 필드는 벡터 DB에서 임베딩 후 자동 저장/관리되는 경우가 많으므로, 입력 데이터에는 없어도 됨
> metadata는 확장성을 위해 object로 설계 (예: { "created_at": "...", "tags": ["..."] })
> level 필드는 계층적 구조 복원, 목차 생성 등에 필요 
> equations, tables, images는 리소스 참조를 위한 배열로, 필요한 경우에만 포함 