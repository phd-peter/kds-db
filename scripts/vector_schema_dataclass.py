from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class ResourceReference:
    """
    리소스 참조 기본 클래스 (수식, 표, 이미지 공통)
    """
    id: str                    # 리소스 고유 ID
    position: Optional[int] = None  # 문단 내 위치 순서

@dataclass
class EquationReference(ResourceReference):
    """
    수식 리소스 참조
    """
    latex: Optional[str] = None  # 수식 LaTeX 표현식 (인라인 수식인 경우)

@dataclass
class TableReference(ResourceReference):
    """
    표 리소스 참조
    """
    caption: Optional[str] = None  # 표 제목
    csv_path: Optional[str] = None  # CSV 파일 경로

@dataclass
class ImageReference(ResourceReference):
    """
    이미지 리소스 참조
    """
    caption: Optional[str] = None  # 이미지 캡션
    path: Optional[str] = None     # 이미지 파일 경로

@dataclass
class VectorRecord:
    """
    벡터 DB 저장용 기본 데이터 모델
    """
    doc_id: str                # 문서 고유 ID (예: 파일명)
    para_id: str               # 문단 고유 ID (doc_id+순번)
    type: str                  # 문단 유형 (header, paragraph, glossary 등)
    text: str                  # 본문 텍스트 (임베딩 대상)
    level: Optional[int] = None  # 헤더일 때만 계층(level) 정보
    term: Optional[str] = None # 용어 정의일 경우 용어명, 일반 문단은 None
    equations: List[EquationReference] = field(default_factory=list)  # 수식 참조 목록
    tables: List[TableReference] = field(default_factory=list)  # 표 참조 목록
    images: List[ImageReference] = field(default_factory=list)  # 이미지 참조 목록
    metadata: Dict[str, Any] = field(default_factory=dict)  # 확장 메타데이터
    vector: Optional[List[float]] = None  # 임베딩 벡터 (DB 저장 시 자동 생성) 