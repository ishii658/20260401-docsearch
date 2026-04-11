from uuid import uuid4
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Record, ScoredPoint

from conver_md_chunk import MdChunk

class vecDataStore:
    def __init__(self, path: str = "./qdrant_data", model_dim: int = 768):
        self.client = QdrantClient(path=path)
        self.model_dim = model_dim
        self.collection: str = ""

    def close(self) -> None:
        """明示的に QdrantClient を閉じる."""
        self.client.close()

    def create_collection(self, collection_name: str) -> int:
        """コレクションを作成.

        すでにあったら作成しない

        Args:
            collection_name (str): コレクション名

        Returns:
            int: コレクションの数
        """
        self.collection = collection_name
        # コレクション一覧を取得
        response = self.client.get_collections()

        # 各コレクション名をリスト化
        collection_names = [c.name for c in response.collections]
        collection_num = len(collection_names)

        # 存在チェック
        if collection_name not in collection_names:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.model_dim,
                    distance=Distance.COSINE
                ),
            )

        return collection_num

    def insert_vector_data(self, vector_list: list[list[float]], chunks :list[MdChunk], collection_name: str) -> None:
        """ベクトルデータを挿入.

        Args:
            vector_list (list[float]): ベクトルのリスト
            chunks list[MdChunk]: MdChunkのリスト
        """
        points = []
        for vector, chunk in zip(vector_list, chunks):
            # uuidを生成
            idx = str(uuid4())
            # chunkをdictに変換してpayloadに格納
            chunk_dict = chunk.model_dump()  # Pydanticのモデルをdictに変換
            points.append(PointStruct(id=idx, vector=vector, payload=chunk_dict))
        # for

        if self.collection == "":
            raise ValueError("Collection is not set. Please create a collection first.")
        
        # ベクトルデータストアに登録
        self.upsert_points(collection_name=collection_name, points=points)

    # def reg_data_list(self, chunks: list[MdChunk]):
    #     """MdChunkのリストをベクトルデータストアに登録する.

    #     Args:
    #         chunks (list[MdChunk]): _description_
    #     """
    #     points = []
    #     for chunk in chunks:
    #         # ここでは、chunk.textをベクトル化する処理が必要
    #         # 例えば、chunk.textをベクトル化してvectorに格納する
    #         vector = self.vectorize_text(chunk.text)

    #         # uuidを生成
    #         idx = str(uuid4())
    #         # chunkをdictに変換してpayloadに格納
    #         chunk_dict = chunk.model_dump()  # Pydanticのモデルをdictに変換
    #         points.append(PointStruct(id=idx, vector=vector, payload=chunk_dict))
    #     # for

    #     # ベクトルデータストアに登録
    #     self.upsert_points(collection_name="my_collection", points=points)
    
    # def vectorize_text(self, text: str) -> list[float]:
    #     """テキストをベクトル化.

    #     Args:
    #         text (str): _description_

    #     Returns:
    #         list[float]: _description_
    #     """
    #     t_vec = self.emb_vector.emb(text)
    #     return t_vec[0]  # ベクトルの最初の要素を返す

    def upsert_points(self, collection_name, points):
        self.client.upsert(collection_name=collection_name, points=points)

    def query_points(self, collection_name, query_vector, limit=10) -> list[ScoredPoint]:
        """
        指定されたクエリベクトルに基づいて、コレクション内から最も類似度の高いポイントを検索します。

        このメソッドはQdrantのコアな近傍探索（Nearest Neighbor Search）を実行します。

        Args:
            collection_name (str): 検索対象のコレクション名。
            query_vector (list[float]): 検索に使用するクエリベクトル（N次元のリスト）。
            limit (int, optional): 取得する結果の最大件数。デフォルトは10です。

        Returns:
            list[Record]: 検索結果のポイント（Recordオブジェクト）のリスト。
                           各RecordにはID、スコア、ペイロードが含まれます。
        """
        result = self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit,
        )
        search_results = result.points

        return search_results
    
    def scroll_points(self, limit=10, with_vectors=False) -> list[Record]:
        """collection から中身を取得

        Args:
            limit (int, optional): Defaults to 10.

        Returns:
            list[Record]: _description_
        """
        data = self.client.scroll(self.collection, limit=limit, with_vectors=with_vectors)
        return data[0]

def test_qdrant():
    # ローカルファイル（ディレクトリ）を指定
    client = QdrantClient(path="./qdrant_data")

    # コレクション作成（ベクトルサイズは例として4次元）
    client.create_collection(
        collection_name="my_collection",
        vectors_config=VectorParams(size=4, distance=Distance.COSINE),
    )

    # データ登録
    points = [
        PointStruct(id=1, vector=[0.1, 0.2, 0.3, 0.4], payload={"text": "hello"}),
        PointStruct(id=2, vector=[0.2, 0.1, 0.4, 0.3], payload={"text": "world"}),
    ]

    client.upsert(collection_name="my_collection", points=points)

    # 検索
    results = client.query_points(
        collection_name="my_collection",
        query=[0.1, 0.2, 0.3, 0.4],
        limit=2,
    )

    for r in results.points:
        print(r.id, r.score, r.payload)

if __name__ == "__main__":
    test_qdrant()