# main.py

from fastapi import FastAPI, WebSocket
import asyncio

app = FastAPI()

@app.websocket("/ws/chat/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    """
    指定されたクライアントIDを持つWebSocketエンドポイント。
    クライアントからのメッセージを受信し、そのままエコーバックします。
    """
    await websocket.accept()
    print(f"Client {client_id} connected.")
    
    try:
        while True:
            # クライアントからのメッセージを待機
            data = await websocket.receive_text()
            
            # 受信したメッセージをログに出力
            print(f"Client {client_id} received: {data}")
            
            # 受信したメッセージをクライアントにエコーバック
            await websocket.send_text(f"Echo: {data}")
            
    except Exception as e:
        # 接続が切断された場合などの例外処理
        print(f"Client {client_id} disconnected with error: {e}")
    finally:
        # 確実に切断処理を行う
        await websocket.close()
        print(f"Client {client_id} disconnected.")

@app.get("/")
async def read_root():
    """
    ルートパスへのアクセス時に簡単なステータスを返す（WebSocket用ではないエンドポイントの確認用）
    """
    return {"message": "WebSocket Chat Sample running. Connect to /ws/chat/{client_id}"}

# 実行方法の提案: uvicorn main:app --reload