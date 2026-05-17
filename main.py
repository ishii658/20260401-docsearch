"""検索アプリ.

# データベース登録文章検索アプリケーション

## アプリケーション概要
このアプリケーションは、データベースに格納された文章データを効率的に検索・管理するためのユーザーインターフェースです。AI モデルを統合することで、高度な自然言語クエリや要約機能を提供します。

## 主な機能

### 1. **全文検索機能**
- データベース内のすべての登録文章を検索

### 2. **AI 支援検索**
- 自然言語での質問に回答（Qwen3.5:9b, Gemma4, Llama など）


## UI コンポーネント

| 画面要素 | 機能説明 |
|---------|----------|
| **検索バー** | キーワード入力、フィルタオプション |
| **結果リスト** | マッチした文章の表示（タイトル、摘要、メタデータ） |
| **詳細ビュー** | 選択した文章の完全な内容と編集機能 |
| **チャットパネル** | AI モデルによる対話的検索支援 |

## システム要件
* python 3.11以上

```
pip install docling docling-core
pip install llama-cpp-python
pip install qdrant-client
```

---

この説明は、アプリケーションの主要な機能を網羅しており、ユーザーが直感的に操作方法を理解できるよう設計されています。


"""
import sys
# 環境変数を読み込み
import os
import sqlite3

from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication, QMainWindow
from ui.main_ui import Ui_MainWindow  # 変換されたクラスをインポート
from qdrant_client import QdrantClient
from lib.gen_emb_vector import embVector

# 環境変数ロード
load_dotenv()
VECTOR_DB_DIR = os.getenv('VECTOR_DB_DIR', 'qdrant_data')
VECTOR_DB_COLLECTION = os.getenv('VECTOR_DB_COLLECTION', 'docvec')
SQLITE_DB = os.getenv('SQLITE_DB', 'words.sqlite3')
WORDS_TABLE = os.getenv('WORDS_TABLE', 'words')


class MyWindow(QMainWindow):
    """ウィンドウクラス."""

    def __init__(self):
        super().__init__()
        # UIのセットアップ
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.con = sqlite3.connect(SQLITE_DB)
        self.cur = self.con.cursor()

        self.ui.pushButton.clicked.connect(self.handle_search)
        self.ui.pushButton_2.clicked.connect(self.handle_search2)

        self.client = QdrantClient(path=VECTOR_DB_DIR)
        self.emb = embVector()

    # デストラクタ
    def __del__(self):
        self.cur.close()
        self.con.close()

    def handle_search(self):
        """ボタンが押されたら検索."""
        # line edit のテキストを取得
        search_query = self.ui.lineEdit.text().strip()

        if not search_query.strip():
            return
        
        # 結果数
        nnum = self.ui.spinBox.value()

        table_name = WORDS_TABLE
        sql = f"SELECT file_path, pages, text FROM {table_name} WHERE text MATCH ? LIMIT {nnum}"
        self.cur.execute(sql, (f'{search_query}',))
        results: list[tuple[str, str, str]] = [row for row in self.cur.fetchall()]
        print(results)
        
        txt = ""
        for row in results:
            txt += f"{row[0]}, {row[1]}, {row[2]}\n"
        self.ui.resulttext.setPlainText(txt)

    def handle_search2(self):
        """文章検索ボタン."""
        # クエリをvectorDBに
        
        #  検索ワードのベクトル化
        query = self.ui.lineEdit_2.text().strip()
        qvec = self.emb.emb(query)

        # 結果数
        nnum = self.ui.spinBox.value()

        # 検索
        # qdrant 検索
        result = self.client.query_points(
            collection_name=VECTOR_DB_COLLECTION,
            query=qvec,
            limit=nnum,
        )
        search_results = result.points

        txt = ""
        for row in search_results:
            payload = row.payload
            if payload is not None:
                text = payload.get("text", "")
                # text から改行を削除
                text_p = text.replace("\n", " ")
                pages = payload.get("pages")
                file_name = payload.get("file_name")
                txt += f"{text_p}, {pages}, {file_name}\n"
        self.ui.resulttext.setPlainText(txt)
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
