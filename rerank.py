# リランキングクラス
#
# # JevEmbed のインストール
# pip install git+https://github.com/HITsz-TMG/JevEmbed.git
# pip install git+https://github.com/HITsz-TMG/JevEmbed.git
# python -m pip install -U "jevembed[local]"
#
# # モデルダウンロード用のツール (huggingface_hub)
# pip install -U "huggingface_hub[cli]"
# # フォルダを作成 (Linux / Mac の場合)
# mkdir -p /models/JevEmbed-Qwen3-Embedding-0.6B
#
# # Hugging Face からローカルディレクトリへダウンロード
# # ダウンロード（hf コマンドを使用）
# hf download HIT-TMG/JevEmbed-Qwen3-Embedding-0.6B \
#   --local-dir /models/JevEmbed-Qwen3-Embedding-0.6B
#
# /models/JevEmbed-Qwen3-Embedding-0.6B/
# ├── jevembed.yaml       <-- これが必須
# ├── config.json
# ├── model.safetensors   <-- モデルの重み本体
# ├── tokenizer.json
# └── ...

import logging
from dataclasses import replace
from pathlib import Path
from typing import Any

from jevembed import JevEmbed, ModelConfig

logger = logging.getLogger(__name__)

# ログ出力の設定（必要に応じて調整）
logging.basicConfig(level=logging.INFO)


# def main():
#     # 1. モデルの初期化 (インスタンス化時にモデルがメモリにロードされます)
#     model_dir = "/models/JevEmbed-Qwen3-Embedding-0.6B"
#     reranker = JevReranker(model_dir=model_dir)

#     # 2. 検索クエリ
#     query = "Qwen3-Embedding-0.6Bとは何ですか？"

#     # 3. 入力ドキュメント（ベクトル検索システム等から取得した結果を想定）
#     # ※ 各辞書には最低限 "text" キーが必要です
#     documents = [
#         {
#             "id": "doc_001",
#             "text": "Qwen3-Embedding-0.6BはAlibabaが公開したEmbeddingモデルです。",
#             "vector_score": 0.85,
#             "category": "AI/LLM",
#         },
#         {
#             "id": "doc_002",
#             "text": "今日は広島県では晴れるでしょう。",
#             "vector_score": 0.42,
#             "category": "Weather",
#         },
#         {
#             "id": "doc_003",
#             "text": "Embeddingモデルは文章をベクトルに変換するために使用されます。",
#             "vector_score": 0.78,
#             "category": "AI/LLM",
#         },
#     ]

#     print(f"--- クエリ: {query} ---\n")

#     # 4. リランキングを実行 (上位2件を取得)
#     results = reranker.rerank(
#         query=query,
#         documents=documents,
#         top_k=2,
#     )

#     # 5. 結果の出力
#     print("--- リランキング結果 (top_k=2) ---")
#     for doc in results:
#         print(f"Rank {doc['rank']}:")
#         print(f"  ID           : {doc['id']}")
#         print(f"  Jev Score    : {doc['jev_score']:.4f}")
#         print(f"  Vector Score : {doc['vector_score']}")
#         print(f"  Category     : {doc['category']}")
#         print(f"  Text         : {doc['text']}")
#         print("-" * 50)


# if __name__ == "__main__":
#     main()

class JevReranker:
    """JevEmbed-Qwen3-Embedding-0.6B を使用した文書リランキングクラス。

    既存のベクトル検索（Vector Search）等で取得されたドキュメント群を受け取り、
    JevEmbed による関連度スコア（relevance score）を算出・付与して再並べ替えを行います。

    モデルはクラスの初期化（`__init__`）時に 1 回のみロードされ、
    `rerank` メソッドの呼び出し時にはロード済みのモデルインスタンスを再利用します。

    Attributes:
        model_dir (Path): ロードされた JevEmbed モデルの絶対パス。
        client (JevEmbed): 評価処理を実行する JevEmbed クライアントインスタンス。
    """

    def __init__(self, model_dir: str|Path) -> None:
        """JevEmbed モデルの設定ファイルを読み込み、クライアントを初期化します。

        Args:
            model_dir (Union[str, Path]): JevEmbed モデルおよび設定ファイル（jevembed.yaml）が
                格納されているローカルディレクトリのパス。

        Raises:
            FileNotFoundError: 指定されたディレクトリ内に `jevembed.yaml` が存在しない場合。
        """
        self.model_dir: Path = Path(model_dir).resolve()
        config_path: Path = self.model_dir / "jevembed.yaml"

        if not config_path.exists():
            raise FileNotFoundError(
                f"jevembed.yaml が見つかりません: {config_path}"
            )

        logger.info("Loading JevEmbed model from: %s", self.model_dir)

        config: ModelConfig = replace(
            ModelConfig.load(config_path),
            model_name_or_path=str(self.model_dir),
        )

        self.client: JevEmbed = JevEmbed(config=config)
        logger.info("JevEmbed model loaded successfully.")

    def rerank(
        self,
        query: str,
        documents: list[dict[str, Any]],
        top_k: int|None = None,
    ) -> list[dict[str, Any]]:
        """クエリに対して事前検索された文書群を JevEmbed で関連度順に並べ替えます。

        Args:
            query (str): 検索対象となるユーザーのクエリ文字列。
            documents (List[Dict[str, Any]]): リランキング対象の文書情報辞書のリスト。
                各要素は最低限 `"text"` キーを含んでいる必要があります。
                例:
                    [
                        {
                            "id": 1,
                            "text": "検索対象の本文...",
                            "vector_score": 0.82
                        },
                        ...
                    ]
            top_k (Optional[int], optional): リランキング結果の上位何件を返すか。
                `None` の場合は全件を返します。デフォルトは `None`。

        Returns:
            List[Dict[str, Any]]: リランキング後の文書辞書リスト。
                各要素には `"jev_score"`（関連度スコア）および `"rank"`（順位: 1始まり）が
                付加され、`jev_score` の降順で並べ替えられます。

        Raises:
            ValueError: `query` が空文字列の場合、`documents` 内の辞書に `"text"` キーが存在しない場合、
                または `top_k` に 1 未満の数値が指定された場合。
            TypeError: `documents` 内の `"text"` の値が文字列（`str`）でない場合。
        """
        if not query.strip():
            raise ValueError("query が空です。有効な検索クエリを指定してください。")

        if not documents:
            return []

        results: list[dict[str, Any]] = []

        for index, document in enumerate(documents):
            if "text" not in document:
                raise ValueError(f"documents[{index}] に 'text' キーが含まれていません。")

            text: Any = document["text"]

            if not isinstance(text, str):
                raise TypeError(
                    f"documents[{index}]['text'] は str 型である必要があります。(指定された型: {type(text).__name__})"
                )

            if not text.strip():
                logger.warning(
                    "インデックス %d の文書テキストが空のため、リランキング処理をスキップします。",
                    index,
                )
                continue

            jev_score: float = self._score(query=query, document=text)

            # 原本のデータ構造を保持するため浅いコピーを作成
            result: dict[str, Any] = dict(document)
            result["jev_score"] = jev_score
            results.append(result)

        # jev_score の降順でソート
        results.sort(key=lambda x: x["jev_score"], reverse=True)

        # リランキング後の順位（1始まり）を付与
        for rank, result in enumerate(results, start=1):
            result["rank"] = rank

        if top_k is not None:
            if top_k < 1:
                raise ValueError("top_k は 1 以上の整数で指定してください。")
            results = results[:top_k]

        return results

    def _score(self, query: str, document: str) -> float:
        """単一のクエリと文書ペアに対して JevEmbed の判定処理を呼び出しスコアを取得します。

        Args:
            query (str): 検索クエリ。
            document (str): 判定対象の文書テキスト。

        Returns:
            float: JevEmbed によって算出された関連度スコア。
        """
        request: dict[str, Any] = {
            "state": {
                "query": query,
                "passage": document,
            },
            "questions": {
                "relevant": {
                    "type": "noul",
                    "instructions": (
                        "Is the passage relevant to the user's query? "
                        "The passage should contain information that "
                        "directly helps answer the query."
                    ),
                    "criteria": {
                        "true": (
                            "The passage is relevant and contains "
                            "useful information for answering the query."
                        ),
                        "false": (
                            "The passage is not relevant or does not "
                            "contain useful information for answering "
                            "the query."
                        ),
                    },
                },
            },
        }

        response: dict[str, Any] = self.client.evaluate(request)
        return self._extract_score(response)

    @staticmethod
    def _extract_score(response: dict[str, Any]) -> float:
        """JevEmbed のレスポンス辞書から関連度スコアを安全に抽出・変換します。

        Args:
            response (dict[str, Any]): JevEmbed の `evaluate()` メソッドから返却されたレスポンス辞書。

        Returns:
            float: 抽出された数値スコア。

        Raises:
            RuntimeError: レスポンスからのスコア抽出および float への変換に失敗した場合。
        """
        try:
            # レスポンス構造の揺れ（`answers` キーの有無など）に柔軟に対応
            answers: dict[str, Any] = response.get("answers", response)
            relevant: dict[str, Any] | float | int | str = answers.get("relevant", {})

            if isinstance(relevant, dict):
                # 主要なスコアキー候補を順次探索
                for key in ("noul", "probability", "score", "value"):
                    val = relevant.get(key)
                    if val is not None:
                        return float(val)

                # dict なのに知っているキーが1つも存在しなかった場合
                raise ValueError(f"辞書内に有効なスコアキーが見つかりませんでした: {relevant}")

            # ここに到達した時点で relevant は float | int | str に確定する（型チェッカーも認識）
            return float(relevant)

        except (KeyError, TypeError, ValueError) as exc:
            logger.error("JevEmbed レスポンスからのスコア解析に失敗しました: %r", response)
            raise RuntimeError(
                "JevEmbed のレスポンスからスコアを正常に抽出できませんでした。"
            ) from exc