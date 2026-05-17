"""Qt Uiを直接読み込んでアプリ実行"""
import os
import sys
import sqlite3

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from lib.gen_emb_vector import embVector

# 環境変数ロード
load_dotenv()
VECTOR_DB_DIR = os.getenv('VECTOR_DB_DIR', 'qdrant_data')
VECTOR_DB_COLLECTION = os.getenv('VECTOR_DB_COLLECTION', 'docvec')
SQLITE_DB = os.getenv('SQLITE_DB', 'words.sqlite3')
WORDS_TABLE = os.getenv('WORDS_TABLE', 'words')

window: QWidget
cur: sqlite3.Cursor
emb: embVector
client: QdrantClient

def main():
    global window
    global cur
    global emb
    global client

    app = QApplication(sys.argv)

    # 1. UI ファイルを開く
    ui_file = QFile("ui/window.ui")
    if not ui_file.open(QFile.ReadOnly):
        print(f"ファイルを開けませんでした: {ui_file.errorString()}")
        sys.exit(-1)

    # 2. ローダーを使って読み込む
    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()

    if not window:
        print(loader.errorString())
        sys.exit(-1)

    con = sqlite3.connect(SQLITE_DB)
    cur = con.cursor()

    window.pushButton.clicked.connect(handle_search)
    window.pushButton_2.clicked.connect(handle_search2)

    client = QdrantClient(path=VECTOR_DB_DIR)
    emb = embVector()

    # 3. 表示
    window.show()
    sys.exit(app.exec())

def handle_search():
    """ボタンが押されたら検索."""
    # line edit のテキストを取得
    search_query = window.lineEdit.text().strip()

    if not search_query.strip():
        return
    
    # 結果数
    nnum = window.spinBox.value()

    table_name = WORDS_TABLE
    sql = f"SELECT file_path, pages, text FROM {table_name} WHERE text MATCH ? LIMIT {nnum}"
    cur.execute(sql, (f'"{search_query}"',))
    results: list[tuple[str, str, str]] = [row for row in cur.fetchall()]
    print(results)
    
    txt = ""
    for row in results:
        txt += f"{row[0]}, {row[1]}, {row[2]}\n"
    window.resulttext.setPlainText(txt)

def handle_search2():
    """文章検索ボタン."""
    # クエリをvectorDBに
    
    #  検索ワードのベクトル化
    query = window.lineEdit_2.text().strip()
    qvec = emb.emb(query)

    # 結果数
    nnum = window.spinBox.value()

    # 検索
    # qdrant 検索
    result = client.query_points(
        collection_name=VECTOR_DB_COLLECTION,
        query=qvec,
        limit=nnum,
    )
    search_results = result.points

    txt = ""
    for row in search_results:
        payload = row.payload
        if payload is not None:
            text = payload.get("text")
            pages = payload.get("pages")
            file_name = payload.get("file_name")
            txt += f"{text}, {pages}, {file_name}\n"
    window.resulttext.setPlainText(txt)

if __name__ == "__main__":
    main()