import sqlite3
con = sqlite3.connect("words.sqlite3")
cur = con.cursor()

table_name = "words"
phrase = "特許"
sql = f"SELECT file_path, pages, text FROM {table_name} WHERE text MATCH ?"
# sql = f"SELECT file_path, pages, text FROM {table_name} LIMIT 10"
# フレーズ検索はクォートで囲む
cur.execute(sql, (f'"{phrase}"',))
# cur.execute(sql)
results: list[tuple[str, str, str]] = [row for row in cur.fetchall()]
print(results)

cur.close()
con.close()