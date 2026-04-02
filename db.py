from uuid import uuid4
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from conver_md_chunk import MdChunk
from gen_emb_vector import embVector

class vecDataStore:
    def __init__(self, path="./qdrant_data"):
        self.client = QdrantClient(path=path)
        # embddding vector生成クラスのインスタンスを作成
        self.emb_vector = embVector()

    def create_collection(self, collection_name: str):
        """コレクションを作成.

        すでにあったら作成しない

        Args:
            collection_name (str): コレクション名
        """
        # コレクション一覧を取得
        response = self.client.get_collections()

        # 各コレクション名をリスト化
        collection_names = [c.name for c in response.collections]

        # 存在チェック
        if collection_name not in collection_names:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.emb_vector.model_dim,
                    distance=Distance.COSINE
                ),
            )

    def reg_data_list(self, chunks: list[MdChunk]):
        """MdChunkのリストをベクトルデータストアに登録する.

        Args:
            chunks (list[MdChunk]): _description_
        """
        points = []
        for chunk in chunks:
            # ここでは、chunk.textをベクトル化する処理が必要
            # 例えば、chunk.textをベクトル化してvectorに格納する
            vector = self.vectorize_text(chunk.text)

            # uuidを生成
            idx = str(uuid4())
            # chunkをdictに変換してpayloadに格納
            chunk_dict = chunk.model_dump()  # Pydanticのモデルをdictに変換
            points.append(PointStruct(id=idx, vector=vector, payload=chunk_dict))
        # for

        # ベクトルデータストアに登録
        self.upsert_points(collection_name="my_collection", points=points)
    
    def vectorize_text(self, text: str) -> list[float]:
        """テキストをベクトル化.

        Args:
            text (str): _description_

        Returns:
            list[float]: _description_
        """
        t_vec = self.emb_vector.emb(text)
        return t_vec[0]  # ベクトルの最初の要素を返す

    def upsert_points(self, collection_name, points):
        self.client.upsert(collection_name=collection_name, points=points)

    def query_points(self, collection_name, query_vector, limit=10):
        return self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit,
        )

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