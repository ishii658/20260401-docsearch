"""検索."""
from lib.gen_emb_vector import embVector
from lib.vecdb import vecDataStore
from lib.llm_test import llmCmp

def main(search_text: str):
    """Main.
    
    Args:
        search_text (str): 検索テキスト
    """
    # 文字列を Vector に変換
    eemb = embVector()
    vector = eemb.emb(search_text)

    # 探す
    vdb = vecDataStore()
    r_points = vdb.query_points("test", vector, 30)

    print("=====================")
    print(search_text)
    print("^^^^^^^^^^^^^^^^^^^^^")
    print("=====================")

    # 結果の評価
    cmp = llmCmp()

    for row in r_points:
        # row.score row.payload.text .headings:list[str]  pages 
        payload = row.payload
        print("============")
        print(f"score:{row.score}")
        print(f"headings: {payload['headings']}" )
        print(f"text: {payload['text']}")

        # 比較
        val = cmp.compare_texts(search_text, payload['text'])
        print(f"llm_score: {val}")
        print("^^^^^^^^^^^")


    # for


if __name__ == "__main__":
    main("特許検索")