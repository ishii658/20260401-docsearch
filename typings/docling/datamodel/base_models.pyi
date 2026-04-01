# typings/docling/datamodel/base_models.pyi

from typing import Any, List

class BaseMeta:
    doc_items: List[Any]  # 実際には DocItem 型だが簡易化
    headings: List[str]
