# typings/docling/datamodel/document_models.pyi

from typing import List, Optional

class Provenance:
    page_no: int

class DocItem:
    prov: Optional[List[Provenance]]

class Document:
    """HierarchicalChunker が扱う最低限の属性"""

    items: List[DocItem]
    headings: List[str]
    text: str
