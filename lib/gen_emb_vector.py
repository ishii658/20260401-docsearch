"""Embedding vector生成."""
from typing import Callable
from llama_cpp import Llama
from lib.conver_md_chunk import MdChunk
from lib.tokenize_keywords import TokenizerKeywords


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

    def emb_chunks(self, chunks: list[MdChunk], tolknize=False, callback: Callable[[str, list[int], str], None] | None = None) -> tuple[list[list[float]], list[list[float]], list[MdChunk]]:
        """MdChunkのリストをEmbedding Vectorのリストに変換.

        Args:
            chunks (list[MdChunk]): MdChunkのリスト
            tolknize (bool): 単語の羅列に変換するかどうか
            callback (Callable[[str, list[int], str], None] | None): コールバック関数. headings,textの動詞名詞をスペース区切りしたものが渡される
                                                                         関数に渡されるのは、 path, ページ, 文字列
        Returns:
           tuple[list[list[float]], list[list[float]]]: Embedding Vectorのリスト
        """
        if tolknize:
            tkn = TokenizerKeywords(dummy=False)
        else:
            tkn = TokenizerKeywords(dummy=True)  # dummyモードで使用する場合、tokenizer_obj は None

        vectors: list[list[float]] = []
        heddings_vectors: list[list[float]] = []

        # chunks をコピー
        cp_chunks: list[MdChunk] = [chunk.model_copy(deep=True) for chunk in chunks]
        for chunk in cp_chunks:
            
            if chunk.headings is not None:
                header_str = " ".join(chunk.headings)
                # 単語分解して登録するか
                if tolknize:
                    w_list = tkn.tokenize(header_str)
                    # 重複削除
                    w_list_new = list(set(w_list))

                    w_list_str = " ".join(w_list_new)
                    header_vector = self.emb(w_list_str)
                    chunk.headings = [w_list_str]

                    pages = chunk.pages
                    file_path = chunk.file_name
                    if callback:
                        callback(file_path, pages, w_list_str)
                else:
                    header_vector = self.emb(header_str)
                heddings_vectors.append(header_vector)
            #

            # 文章を単語に分解して登録するか
            if tolknize:
                w_list = tkn.tokenize(chunk.text)
                # 重複削除
                w_list_new = list(set(w_list))

                w_list_str = " ".join(w_list_new)
                vector = self.emb(w_list_str)
                chunk.text = w_list_str

                pages = chunk.pages
                file_path = chunk.file_name
                if callback:
                    callback(file_path, pages, w_list_str)
            else:
                vector = self.emb(chunk.text)
            vectors.append(vector)

        return vectors, heddings_vectors, cp_chunks

if __name__ == "__main__":
    g_txt = "こんいちは"
    g_ev = embVector()
    try:
        vec = g_ev.emb(g_txt)
        print(vec)
    finally:
        g_ev.close()
