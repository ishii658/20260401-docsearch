"""ファイル(xlsx,pptx.pdf)などを読み込んでchunkに別れたMarkdownに."""

import json
from pathlib import Path

from docling.chunking import HierarchicalChunker
from docling.document_converter import DocumentConverter
from pydantic import BaseModel


class MdChunk(BaseModel):
    """Chunk分割結果."""

    headings: list[str] | None
    """上位のセクション"""
    text: str
    """文字列"""
    pages: list[int]
    """ページリスト."""
    file_name: str
    """ファイル名"""

class convertMdChunk:
    """ファイル(xlsx,pptx.pdf)などを読み込んでchunkに別れたMarkdownに."""

    def __init__(self) -> None:
        self.converter: DocumentConverter = DocumentConverter()

    def convert(self, file_path: str) -> list[MdChunk]:
        """Markdown chunkに変換"""
        result = self.converter.convert(Path(file_path))
        chunker = HierarchicalChunker()
        chunk_obj = chunker.chunk(result.document)
        chunks = list(chunk_obj)

        # {headings:str, text:str, pages:list[int]}
        ret_chunk: list[MdChunk] = []
        for chunk in chunks:
            meta = chunk.meta
            page_numbers: set[int] = set()
            chunk.meta
            for item in chunk.meta.doc_items:
                # meta.headings
                # prov (Provenance) が存在し、中身があるか確認
                if hasattr(item, "prov") and item.prov:
                    for p in item.prov:
                        # page_no は 1 から始まる数値
                        page_numbers.add(p.page_no)

            md_chunk = MdChunk(
                headings=meta.headings,
                text=chunk.text,
                pages=sorted(list(page_numbers)),
                file_name=file_path
            )
            ret_chunk.append(md_chunk)
        #
        return ret_chunk


if __name__ == "__main__":
    cnv = convertMdChunk()
    cnv.convert("/home/ishii/data/pat.pptx")
