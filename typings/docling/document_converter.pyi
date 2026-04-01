# typings/docling/document_converter.pyi

from pathlib import Path
from typing import Optional, Tuple

from datamodel.document_models import Document

class ConversionResult:
    """convert() の返却オブジェクト"""

    @property
    def document(self) -> Document: ...
    # これで Pyright は document が必ず存在することを認識

class DocumentConverter:
    def convert(
        self,
        source: Path | str,
        headers: Optional[dict[str, str]] = None,
        raises_on_error: bool = True,
        max_num_pages: int = ...,
        max_file_size: int = ...,
        page_range: Tuple[int, int] = ...,
    ) -> ConversionResult: ...
