"""Embedding Vector生成 と データベースへの保存."""
from glob import glob
from vecdb import vecDataStore
from gen_emb_vector import embVector
from conver_md_chunk import MdChunk, convertMdChunk

from tokenize_keywords import TokenizerKeywords

def search_dir(dir_path: str, extensions: list[str]) -> list[str]:
    """ディレクトリ内のファイルを検索.

    Args:
        dir_path (str): ディレクトリのパス
    """
    # globを使用して、ディレクトリ内のすべてのファイルを検索
    # 対応する拡張子のファイルを検索
    file_paths = []
    for ext in extensions:
        file_paths.extend(glob(f"{dir_path}/**/*{ext}", recursive=True))
    return file_paths

def gen_emb_db(file_path: str, collection_name: str) -> None:
    """Embedding Vector生成 と データベースへの保存.
    
    指定したディレクトリのファイルを検索し、Embedding Vectorを生成して、データベースに保存する.
    Args:
        file_path (str): ファイルのパス
        collection_name (str): コレクション名
    """
    # ファイルリストを取得
    file_paths = search_dir(file_path, extensions=[".pptx", "xlsx", ".docx", ".pdf", ".md"])

    # ファイルをMdChunkのリストに変換するクラス
    cnv_md_chunk = convertMdChunk()

    # ファイルをMdChunkのリストに変換
    # docling を使って ファイルを Markdown chunk に変換する処理
    md_chunks_list: list[list[MdChunk]] = []
    for file_path in file_paths:
        # ファイルをMdChunkのリストに変換する処理
        chunks = cnv_md_chunk.convert(file_path)
        md_chunks_list.append(chunks)
    # for
    
    # embVectorのインスタンスを作成
    emb_vector = embVector()
    vdb = vecDataStore(model_dim=emb_vector.model_dim)

    try:
        # embedding vector 生成
        vectors_list: list[list[list[float]]] = []
        header_vectors_list:list[list[list[float]]] = []

        kw_chunk_list: list[list[MdChunk]] = []
        kw_vectors_list: list[list[list[float]]] = []
        kw_header_vectors_list:list[list[list[float]]] = []
        for md_chunks in md_chunks_list:
            # MdChunkのリストからテキストを抽出
            # テキストからEmbedding Vectorを生成
            vectors, heddings_vectors, _ = emb_vector.emb_chunks(md_chunks)
            vectors_list.append(vectors)
            header_vectors_list.append(heddings_vectors)

            # テキストを形態素に分割して、名詞と動詞を取り出して Embedding Vectorを生成
            kw_vectors, kw_heddings_vectors, kw_chunk = emb_vector.emb_chunks(md_chunks, tolknize=True)
            kw_chunk_list.append(kw_chunk)
            kw_vectors_list.append(vectors)
            kw_header_vectors_list.append(kw_heddings_vectors)

        # === DB への書き込み ===

        # heddings 用コレクション
        headdings_collection = f"{collection_name}_headdings"

        # kw 用コレクション
        kw_collection = f"kw_{collection_name}"
        kw_headdings_collection = f"kw_{collection_name}_headdings"

        # 内容のvector
        vdb.create_collection(collection_name)
        # heddings のvector
        vdb.create_collection(headdings_collection)
        # kw のvector
        vdb.create_collection(kw_collection)
        vdb.create_collection(kw_headdings_collection)

        for idx, vectors in enumerate(vectors_list):
            header_vectors = header_vectors_list[idx]
            chunk = md_chunks_list[idx]
            vdb.insert_vector_data(vectors, chunk, collection_name)
            vdb.insert_vector_data(header_vectors, chunk, headdings_collection)

            # キーワード用
            kw_chunk = kw_chunk_list[idx]
            kw_vectors = kw_vectors_list[idx]
            kw_header_vectors =kw_header_vectors_list[idx]
            vdb.insert_vector_data(kw_vectors, kw_chunk, kw_collection)
            vdb.insert_vector_data(kw_header_vectors, kw_chunk, kw_headdings_collection)
    finally:
        emb_vector.close()
        vdb.close()

if __name__ == "__main__":
    gen_emb_db(file_path="/home/ishii/data", collection_name="test")