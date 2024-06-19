from flask import Flask, request
from synochat.webhooks import OutgoingWebhook
import pandas as pd
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

app = Flask(__name__)

# ログ設定
logging.basicConfig(level=logging.DEBUG)

# 環境変数を読み込む
load_dotenv()
token = os.getenv("SYNOLOGY_CHAT_TOKEN")
tag_to_excel = {
    os.getenv("TAG_1"): os.getenv("EXCEL_1"),
    os.getenv("TAG_2"): os.getenv("EXCEL_2"),
    os.getenv("TAG_3"): os.getenv("EXCEL_3"),
    os.getenv("TAG_4"): os.getenv("EXCEL_4"),
    os.getenv("TAG_5"): os.getenv("EXCEL_5"),
    os.getenv("TAG_6"): os.getenv("EXCEL_6"),
    os.getenv("TAG_7"): os.getenv("EXCEL_7"),
}


@app.route("/echo", methods=["POST"])
def echo():
    logging.debug("Received a POST request")

    try:
        webhook = OutgoingWebhook(request.form, token, verbose=True)
    except Exception as e:
        logging.error(f"Failed to create OutgoingWebhook: {e}")
        return "Failed to create OutgoingWebhook", 500

    if not webhook.authenticate(token):
        logging.error("Token mismatch")
        return "Outgoing Webhook authentication failed: Token mismatch.", 403

    logging.debug(f"Webhook data: {webhook}")

    # タイムスタンプ、投稿者名、投稿内容を取得してエクセルに記録
    try:
        timestamp = int(webhook.timestamp) / 1000  # ミリ秒から秒に変換
        dt = datetime.fromtimestamp(timestamp)
        username = webhook.username
        text = webhook.text

        # タグに基づいてエクセルファイルを選択
        excel_file_path = next(
            (excel_file for tag, excel_file in tag_to_excel.items() if tag in text),
            None,
        )

        if not excel_file_path:
            return "No matching tag found.", 200

        # 新規データをDataFrameにまとめる
        new_data = pd.DataFrame(
            {
                "Date": [dt],
                "Username": [username],
                "Text": [text],
            }
        )

        # エクセルファイルに追記または新規作成
        if not os.path.exists(excel_file_path):
            new_data.to_excel(excel_file_path, index=False)
            logging.debug("Excel file created and data recorded")
        else:
            # 既存のデータを読み込む
            with pd.ExcelWriter(
                excel_file_path, engine="openpyxl", mode="a", if_sheet_exists="overlay"
            ) as writer:
                new_data.to_excel(
                    writer,
                    index=False,
                    header=False,
                    startrow=writer.sheets["Sheet1"].max_row,
                )
            logging.debug("Data appended to existing Excel file")

        return "Timestamp, username, and text recorded.", 200
    except Exception as e:
        logging.error(f"Failed to record data: {e}")
        return "Failed to record data", 500


if __name__ == "__main__":
    app.run("0.0.0.0", port=5001, debug=True)
