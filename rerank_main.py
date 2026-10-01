"""Rerankクラスのテスト用."""
from rerank import JevReranker


def main():
    # 1. モデルの初期化 (インスタンス化時にモデルがメモリにロードされます)
    model_dir = "/models/JevEmbed-Qwen3-Embedding-0.6B"
    reranker = JevReranker(model_dir=model_dir)

    # 2. 検索クエリ
    query = "Qwen3-Embedding-0.6Bとは何ですか？"

    # 3. 入力ドキュメント（ベクトル検索システム等から取得した結果を想定）
    # ※ 各辞書には最低限 "text" キーが必要です
    documents = [
        {
            "id": "doc_001",
            "text": "Qwen3-Embedding-0.6BはAlibabaが公開したEmbeddingモデルです。",
            "vector_score": 0.85,
            "category": "AI/LLM",
        },
        {
            "id": "doc_002",
            "text": "今日は広島県では晴れるでしょう。",
            "vector_score": 0.42,
            "category": "Weather",
        },
        {
            "id": "doc_003",
            "text": "Embeddingモデルは文章をベクトルに変換するために使用されます。",
            "vector_score": 0.78,
            "category": "AI/LLM",
        },
    ]

    print(f"--- クエリ: {query} ---\n")

    # 4. リランキングを実行 (上位2件を取得)
    results = reranker.rerank(
        query=query,
        documents=documents,
        top_k=3,
    )

    # 5. 結果の出力
    print("--- リランキング結果 (top_k=2) ---")
    for doc in results:
        print(f"Rank {doc['rank']}:")
        print(f"  ID           : {doc['id']}")
        print(f"  Jev Score    : {doc['jev_score']:.4f}")
        print(f"  Vector Score : {doc['vector_score']}")
        print(f"  Category     : {doc['category']}")
        print(f"  Text         : {doc['text']}")
        print("-" * 50)


if __name__ == "__main__":
    main()
