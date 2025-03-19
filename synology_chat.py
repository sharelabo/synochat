# Synology ChatからのWebhookを受信し、メッセージをJSONファイルに保存するアプリケーション
# Dockerコンテナとして実行することを前提とした設計

import logging
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# ログ設定
fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=fmt)
logger = logging.getLogger(__name__)

# 環境変数を読み込む
load_dotenv()
token = os.getenv("SYNOLOGY_CHAT_TOKEN")

# Flaskアプリケーションの初期化
app = Flask(__name__)

# JSONメッセージを保存するファイル
MESSAGES_FILE = os.getenv("MESSAGES_FILE", "received_messages.json")


def verify_token(received_token):
    """トークンを検証する関数"""
    return token == received_token


@app.route("/webhook", methods=["POST"])
def webhook_receiver():
    """Webhookを受信し、JSONファイルに保存する"""
    logger.info(f"Webhookリクエストを受信しました: {request.method}")
    logger.info(f"リクエストヘッダー: {dict(request.headers)}")

    try:
        # リクエストデータの処理
        if request.is_json:
            data = request.get_json()
            logger.info("JSONデータを受信しました")
        else:
            data = request.form.to_dict()
            logger.info(f"フォームデータを受信しました: {data}")
            # リクエストボディも表示
            try:
                raw_data = request.get_data().decode("utf-8")
                logger.info(f"リクエストボディ(生): {raw_data}")
            except Exception:
                logger.info("リクエストボディのデコードに失敗しました")

        logger.debug(f"受信データ: {data}")

        # トークンの検証
        received_token = data.get("token")
        logger.info(f"受信したトークン: {received_token}")
        logger.info(f"期待するトークン: {token}")

        if not verify_token(received_token):
            logger.warning("トークンが一致しません")
            error_resp = {"status": "error", "message": "Invalid token"}
            return jsonify(error_resp), 403

        # 現在時刻を追加
        data["received_at"] = datetime.now().isoformat()

        # メッセージファイルのディレクトリを確認
        messages_dir = os.path.dirname(MESSAGES_FILE)
        if messages_dir and not os.path.exists(messages_dir):
            os.makedirs(messages_dir, exist_ok=True)
            logger.info(f"ディレクトリを作成しました: {messages_dir}")

        # 既存のメッセージを読み込む
        messages = []
        if os.path.exists(MESSAGES_FILE):
            try:
                with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
                    messages = json.load(f)
            except Exception as e:
                logger.error(f"メッセージファイルの読み込みに失敗しました: {e}")

        # 新しいメッセージを追加
        messages.append(data)

        # メッセージを保存
        with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)

        logger.info(f"メッセージをファイルに保存しました: {MESSAGES_FILE}")
        return jsonify({"status": "ok", "message": "Message received"}), 200

    except Exception as e:
        logger.error(f"Webhookの処理中にエラーが発生しました: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


def run_server(host="0.0.0.0", port=5001):
    """Webhookサーバーを実行する関数"""
    logger.info(f"Webhookサーバーを起動します: http://{host}:{port}/webhook")
    logger.info(f"メッセージの保存先: {MESSAGES_FILE}")
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    # サーバーモード
    port = int(os.getenv("PORT", 5001))
    run_server(port=port)
