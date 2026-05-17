"""Sqlite FTS5を使って全文検索."""
import sqlite3
import json

class TxtSerch:
    """Sqlite FTS5を使って全文検索."""
    def __init__(self, db_path: str) -> None:
        """コンストラクタ.

        Args:
            db_path (str): sqlite DBパス
        """
        self.db = sqlite3.connect(db_path)
        self.cursor = self.db.cursor()
        self.table_name = ""

    # デストラクタ
    def __del__(self) -> None:
        """デストラクタ."""
        self.cursor.close()
        self.db.close()

    def begin(self):
        """トランザクションスタート."""
        self.cursor.execute("BEGIN")

    def commit(self):
        """Commit."""
        self.db.commit()

    def create_table(self, table_name: str) -> None:
        """テーブル作成.
        
        Args:
            table_name (str) テーブル名
        """
        # path, ページ, 文字列 のテーブル
        # 
        sql = (
            f'CREATE VIRTUAL TABLE IF NOT EXISTS '
            f'{table_name} USING fts5('
            f'file_path UNINDEXED, '
            f'pages UNINDEXED, '
            f'text, '
            f'tokenize="unicode61");'
        )
        self.cursor.execute(sql)
        self.db.commit()
        self.table_name = table_name

    def insert(self, file_path: str, pages: list[int], text: str) -> None:
        """DBに登録.
        commit は行わないので外側で行うこと.

        Args:
            file_path (str): ファイルパス
            pages (list[int]): ページリスト
            text (str): テキスト
        """
        # pages を文字列化
        pages_str = json.dumps(pages)
        
        sql = (
            f"INSERT INTO {self.table_name} (file_path, pages, text) "
            f"VALUES (?, ?, ?)"
        )
        self.cursor.execute(sql, (file_path, pages_str, text))

    def delete_file(self, file_path: str) -> None:
        """file_path のデータを削除.

        Args:
            file_path (str): ファイルパス
        """
        sql = f"DELETE FROM {self.table_name} WHERE file_path = ?"
        self.cursor.execute(sql, (file_path,))
        self.commit()
        
    def search_word(self, phrase: str) -> list[tuple[str, str, str]]:
        """word を含むデータを検索.

        Args:
           word (str): 検索ワード
        
        Returns:
            データのリスト. 以下の順番のtupleのリスト
                * file_path: ファイルパス
                * pages: ページ数
                * text: 文章
        """
        sql = f"SELECT file_path, pages, text FROM {self.table_name} WHERE text MATCH ?"
        # フレーズ検索はクォートで囲む
        self.cursor.execute(sql, (f'"{phrase}"',))
        results: list[tuple[str, str, str]] = [row[0] for row in self.cursor.fetchall()]
        return results