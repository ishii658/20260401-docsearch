"""LLMのテスト."""
# #%%
from llama_cpp import Llama, LlamaGrammar  # ← これが必要

def test():
    # GGUFモデルのパス
    MODEL_PATH = "./Qwen3.5-4B-Q4_K_M.gguf"
    # MODEL_PATH = "./Qwen3.5-0.8B-Q4_K_M.gguf"
    # MODEL_PATH = "./google_gemma-4-E2B-it-Q4_K_M.gguf"

    # #%%
    # モデル読み込み
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,   
        n_threads=4,
        verbose=False # ログを非表示にしたい場合はFalse
    )

    cc_str = "pythonについて"

    # #%%
    prompts = [
        "Pythonとはプログラミング言語である",
        "日本の首都は東京です",
        "富士山の高さは3000mです",
    ]

    grammar = LlamaGrammar.from_string(r"""
    root ::= "{" ws "\"relevance_score\"" ws ":" ws number ws "}"
    number ::= ("0" | "1" | "0." digit+)
    digit ::= [0-9]
    ws ::= [ \t\n]*
    """)

    # #%%
    for i, prompt in enumerate(prompts, 1):
        print(f"\n=== 実行 {i} : {prompt} ===")
        
        full_prompt = f"""
    You are a strict JSON generator.

    Return ONLY valid JSON.

    Task:
    二つの文章に関連性が大きいかどうか評価してください。

    Scoring rule:
    - 1.0 = 関連性大
    - 0.7 = 関連性中
    - 0.0 = 関連性小

    Text1: {cc_str}
    Text2: {prompt}

    First, think briefly.
    Then output JSON only.

    Format:
    {{"relevance_score": float}}
        """

        full_prompt = f"""
    You are a strict JSON generator.

    Return ONLY valid JSON.

    Task:
    Text1, Text2 の文章の関連度を数値にしてください.
    0 から 1 の数値で、1が関連度が高い評価をしてください。

    Text1: {cc_str}
    Text2: {prompt}

    First, think briefly.
    Then output JSON only.

    Format:
    {{"relevance_score": float}}
        """

        output = llm(
            full_prompt,
            max_tokens=50,
            temperature=0.6,
            top_p=1.0,
            grammar=grammar
        )
        
        result = output["choices"][0]["text"].strip()
        print(result)


    # #%%
    # 連続で実行
    for i, prompt in enumerate(prompts, 1):
        print(f"\n=== 実行 {i} : {prompt} ===")
        
        # チャット形式のプロンプトを構成（Qwen向け）
        # ※単純な llm(prompt) よりも回答が安定します
        full_prompt = f"User: {prompt}\nAssistant: "
        
        output = llm(
            full_prompt,
            max_tokens=256,   # 少し多めにしておくと安心
            echo=False,        # 入力プロンプトを結果に含めない
            repeat_penalty=1.1, # 1.1〜1.2 程度に設定すると繰り返しを抑制できる
            stop=["Assistant:", "User:", "<|im_end|>", "\n\n"]
        )
        
        result = output["choices"][0]["text"].strip()
        print(result)
    # #%%


class llmCmp:
    """LLMを使って選択を評価."""

    llm_model: str = "./Qwen3.5-4B-Q4_K_M.gguf"
    """LLMモデルファイル。"""

    def __init__(self):
        """コンストラクタ."""
        # モデル読み込み
        self.llm = Llama(
            model_path=self.llm_model,
            n_ctx=2048,   
            n_threads=4,
            verbose=False # ログを非表示にしたい場合はFalse
        ) 
    
        # 返却値の制約
        self.grammar = LlamaGrammar.from_string(r"""
root ::= "{" ws "\"relevance_score\"" ws ":" ws number ws "}"
number ::= ("0" | "1" | "0." digit+)
digit ::= [0-9]
ws ::= [ \t\n]*
""")


    def _gen_prompt(self, src_str: str, tgt_str: str) -> str:
        """クエリ用の文字列を返す.

        Args:
            src_str: 比較元文章
            tgt_str: 比較先文章
        """
        full_prompt = f"""
You are a strict JSON generator.

Return ONLY valid JSON.

Task:
Text1, Text2 の文章の関連度を数値にしてください.
0 から 1 の数値で、1が関連度が高い評価をしてください。

Text1: {src_str}
Text2: {tgt_str}

First, think briefly.
Then output JSON only.

Format:
{{"relevance_score": float}}
        """

        return full_prompt
    # def _gen_prompt(self, src_str: str, tgt_str: str) -> str:

    # ２つの文章を比較して関連度を出す
    def compare_texts(self, src_str: str, tgt_str: str) -> dict[str, float]:
        """2つの文章の関連度を計算する.

        Args:
            src_str (str): 比較元文章
            tgt_str (str): 比較対象文章

        Returns:
            dict: 関連度スコアとその詳細
                  {"relevance_score": float}
        """
        full_prompt = self._gen_prompt(src_str, tgt_str)

        output = self.llm(
            full_prompt,
            max_tokens=50,
            temperature=0.6,
            top_p=1.0,
            grammar=self.grammar
        )
        
        result: dict[str, float] = output["choices"][0]["text"].strip() # pyright: ignore[reportAssignmentType, reportIndexIssue]
        return result