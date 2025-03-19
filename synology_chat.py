# Synology ChatからのWebhookを受信し、メッセージをJSONファイルに保存するアプリケーション
# Dockerコンテナとして実行することを前提とした設計

import logging
import os
import json
from datetime import datetime, date
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# ログ設定
fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=fmt)
logger = logging.getLogger(__name__)

# 環境変数を読み込む
load_dotenv()
token = os.getenv("SYNOLOGY_CHAT_TOKEN")
timezone = os.getenv("TIMEZONE", "Asia/Tokyo")  # デフォルトは日本時間

# Flaskアプリケーションの初期化
app = Flask(__name__)

# JSONメッセージを保存するディレクトリ
DATA_DIR = os.getenv("DATA_DIR", "data")


def get_period_start_end(dt):
    """日付から期間の開始日と終了日を取得"""
    current_date = dt.date()
    if current_date.day <= 10:
        # 前月11日から今月10日
        if current_date.month == 1:
            start_date = date(current_date.year - 1, 12, 11)
        else:
            start_date = date(current_date.year, current_date.month - 1, 11)
        end_date = date(current_date.year, current_date.month, 10)
    else:
        # 今月11日から来月10日
        if current_date.month == 12:
            end_date = date(current_date.year + 1, 1, 10)
        else:
            end_date = date(current_date.year, current_date.month + 1, 10)
        start_date = date(current_date.year, current_date.month, 11)
    return start_date, end_date


def get_period_filename(start_date, end_date, extension=".json"):
    """期間に基づいてファイル名を生成"""
    return (
        f"messages_{start_date.strftime('%Y%m')}_{start_date.day:02d}-"
        f"{end_date.strftime('%Y%m')}_{end_date.day:02d}{extension}"
    )


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

        # 現在時刻を追加（タイムゾーン付き）
        now = datetime.now(ZoneInfo(timezone))

        # メッセージの送信時刻を取得（Synology Chatから提供される場合）
        message_timestamp = data.get("timestamp")
        message_time = None  # 初期値として None を設定
        if message_timestamp:
            try:
                # Unix timestampをJST時刻に変換
                message_time = datetime.fromtimestamp(
                    float(message_timestamp), ZoneInfo(timezone)
                )
                data["message_time"] = message_time.isoformat()
                logger.info(f"メッセージ送信時刻: {data['message_time']}")
            except (ValueError, TypeError) as e:
                logger.warning(f"送信時刻の解析に失敗: {e}")

        # 受信時刻を記録
        data["received_at"] = now.isoformat()
        logger.info(f"メッセージ受信時刻: {data['received_at']}")

        # 期間に基づいてファイル名を生成（メッセージ送信時刻を優先）
        target_time = message_time if message_time is not None else now
        start_date, end_date = get_period_start_end(target_time)

        # ファイル名を生成
        filename = get_period_filename(start_date, end_date)
        current_file = os.path.join(DATA_DIR, filename)
        logger.info(f"保存先ファイル: {filename}")

        # メッセージファイルのディレクトリを確認
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR, exist_ok=True)
            logger.info(f"ディレクトリを作成しました: {DATA_DIR}")

        # 既存のメッセージを読み込む
        messages = []
        if os.path.exists(current_file):
            try:
                with open(current_file, "r", encoding="utf-8") as f:
                    messages = json.load(f)
            except Exception as e:
                logger.error(f"メッセージファイルの読み込みに失敗しました: {e}")

        # 新しいメッセージを追加
        messages.append(data)

        # メッセージを保存
        with open(current_file, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)

        logger.info(f"メッセージをファイルに保存しました: {current_file}")
        return jsonify({"status": "ok", "message": "Message received"}), 200

    except Exception as e:
        logger.error(f"Webhookの処理中にエラーが発生しました: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


def run_server(host="0.0.0.0", port=5001):
    """Webhookサーバーを実行する関数"""
    logger.info(f"Webhookサーバーを起動します: http://{host}:{port}/webhook")
    logger.info(f"メッセージの保存先ディレクトリ: {DATA_DIR}")
    logger.info(f"使用タイムゾーン: {timezone}")
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    # サーバーモード
    port = int(os.getenv("PORT", 5001))
    run_server(port=port)
