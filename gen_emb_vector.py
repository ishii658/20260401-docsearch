"""Embedding vector生成."""

from llama_cpp import Llama
from conver_md_chunk import MdChunk

class embVector:
    """Embedding Vector生成."""

    model_path: str = "./embeddinggemma-300M-Q8_0.gguf"

    # モデルの次元数
    model_dim: int = 768
    """モデルの次元数"""

    def __init__(self) -> None:
        self.llm: Llama = Llama(
            model_path=self.model_path, embedding=True, verbose=False
        )

    def close(self) -> None:
        """明示的に llama_cpp リソースを閉じる."""
        self.llm.close()

    def emb(self, text: str) -> list[float]:
        """Embedding Vector 生成.

        Args:
            text (str) 文字列
        """
        embed = self.llm.create_embedding(text)
        vector = embed["data"][0]["embedding"]
        return vector

    def emb_chunks(self, chunks: list[MdChunk]) -> list[list[float]]:
        """MdChunkのリストをEmbedding Vectorのリストに変換.

        Args:
            chunks (list[MdChunk]): MdChunkのリスト
        """
        vectors: list[list[float]] = []
        for chunk in chunks:
            vector = self.emb(chunk.text)
            vectors.append(vector)
        return vectors

if __name__ == "__main__":
    g_txt = "こんいちは"
    g_ev = embVector()
    try:
        vec = g_ev.emb(g_txt)
        print(vec)
    finally:
        g_ev.close()
