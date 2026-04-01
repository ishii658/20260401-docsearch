"""Embedding vector生成."""

from llama_cpp import Llama


class embVector:
    """Embedding Vector生成."""

    model_path: str = "./embeddinggemma-300M-Q8_0.gguf"

    def __init__(self) -> None:
        self.llm: Llama = Llama(
            model_path=self.model_path, embedding=True, verbose=False
        )

    def emb(self, text: str) -> list[list[float]]:
        """Embedding Vector 生成.

        Args:
            text (str) 文字列
        """
        embed = self.llm.create_embedding(text)
        vector_tmp = embed["data"][0]["embedding"]

        # ベクトルが list[float] の場合、[vector] にラップして返す
        if isinstance(vector_tmp[0], list):
            vector = [vector_tmp]
        else:
            vector = vector_tmp

        return vector


if __name__ == "__main__":
    g_txt = "こんいちは"
    g_ev = embVector()
    vec = g_ev.emb(g_txt)
    print(vec)
