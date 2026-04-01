# typings/docling/chunking/base_chunk.pyi

from typing import List

from docling.datamodel.base_models import BaseMeta
from docling.datamodel.document_models import Document

class BaseChunk:
    text: str
    meta: BaseMeta

class HierarchicalChunker:
    def chunk(self, dl_doc: Document) -> list[BaseChunk]: ...
