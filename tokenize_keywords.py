"""文章を単語の羅列に変換.

chunk化されたある程度短い文章を想定
"""
from sudachipy import dictionary, tokenizer

class TokenizerKeywords:
    def __init__(self, dummy=True) -> None:
        """コンストラクタ.

        ダミーモードで使用する場合、tokenizer_obj は None
        """
        self.dummy = dummy
        if not dummy:
            self.tokenizer_obj = dictionary.Dictionary().create()
            self.mode = tokenizer.Tokenizer.SplitMode

    def tokenize(self, text: str) -> list[str]:
        """文章を単語の羅列に変換.

        Args:
            text (str) 入力文章

        Returns:
            単語のリスト
        """
        if self.dummy:
            return []
        # 分割モードを選ぶ（A=細かい、B=中間、C=大きい）
        tokens = self.tokenizer_obj.tokenize(text, self.mode.C)

        nouns: list[str] = []
        verbs: list[str] = []

        for m in tokens:
            pos = m.part_of_speech()[0]  # 品詞の大分類（名詞・動詞など）

            if pos == "名詞":
                nouns.append(m.surface())
            elif pos == "動詞":
                verbs.append(m.dictionary_form())  # 動詞は原形を取得

        # 動詞配列と名詞配列を結合
        combined_keywords = nouns + verbs
        return combined_keywords